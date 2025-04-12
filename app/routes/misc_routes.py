from flask import Blueprint, render_template, redirect, url_for, request, flash
from markupsafe import Markup
from flask_login import login_required, current_user
import markdown
import os
from app import db, csrf
from app.models import TodoList, TodoListAssignment, TodoItem, User, Group, SchoolClass, Homework, HomeworkCompletion, Rubrique
from sqlalchemy import or_
from datetime import datetime

misc_bp = Blueprint('misc', __name__)

@misc_bp.route('/documentation')
@misc_bp.route('/documentation/<path:page>')
@login_required
def documentation(page=None):
    # Seuls admin et prof peuvent accéder
    if current_user.role not in ['admin', 'professeur']:
        flash("Accès réservé aux professeurs et administrateurs.")
        return redirect(url_for('dashboard.home'))
    # Déterminer le fichier à charger
    if not page:
        page = "index"
    # Sécurité : empêcher l'accès à des fichiers hors du dossier
    safe_page = page.replace("..", "").replace("\\", "/")
    doc_path = os.path.join(os.path.dirname(__file__), '../../mode_emploi', safe_page + '.md')
    try:
        with open(doc_path, encoding='utf-8') as f:
            md_content = f.read()
        # Réécriture des liens Markdown pour pointer vers la route Flask
        import re
        def rewrite_links(md):
            # [texte](autre_page.md) ou [texte](autre_page) → [texte](/documentation/autre_page)
            import re
            # D'abord les liens avec .md
            md = re.sub(
                r'\[([^\]]+)\]\(([^)]+)\.md\)',
                lambda m: f'[{m.group(1)}]({url_for("misc.documentation", page=m.group(2))})',
                md
            )
            # Puis les liens sans extension (pas d'URL absolue ni d'ancre)
            md = re.sub(
                r'\[([^\]]+)\]\((?!http[s]?://|/|#)([^)]+)\)',
                lambda m: f'[{m.group(1)}]({url_for("misc.documentation", page=m.group(2))})',
                md
            )
            return md
        md_content = rewrite_links(md_content)
        html_content = Markup(markdown.markdown(md_content, extensions=['tables', 'fenced_code']))
    except Exception as e:
        html_content = Markup(f"<p>Erreur lors du chargement de la documentation : {e}</p>")
    return render_template('documentation.html', doc_content=html_content)

# TODO routes
@misc_bp.route('/todo', methods=['GET'])
@login_required
def todo():
    my_lists = TodoList.query.filter_by(owner_id=current_user.id).all()

    shared_lists = (
        TodoList.query.join(TodoListAssignment)
        .filter(TodoListAssignment.user_id == current_user.id)
        .all()
    )
    
    # Récupérer les devoirs assignés à l'élève
    homework_list = []
    if current_user.role == 'eleve':
        # Récupérer la classe de l'élève (directement ou via son groupe)
        student_class_id = current_user.class_id
        if student_class_id is None and current_user.group_id is not None:
            # Si l'élève n'a pas de classe directement assignée mais est dans un groupe,
            # récupérer la classe du groupe
            group = Group.query.get(current_user.group_id)
            if group:
                student_class_id = group.class_id
        
        # Récupérer les devoirs assignés à la classe ou au groupe de l'élève
        homework_query = Homework.query.filter(
            or_(
                Homework.class_id == student_class_id,
                Homework.group_id == current_user.group_id
            )
        )
        
        # Pour chaque devoir, vérifier si l'élève l'a déjà marqué comme fait
        for homework in homework_query.all():
            # Vérifier si l'élève a déjà marqué ce devoir comme fait
            completion = HomeworkCompletion.query.filter_by(
                homework_id=homework.id,
                student_id=current_user.id
            ).first()
            
            # Ajouter des informations supplémentaires pour l'affichage
            homework_data = {
                'id': homework.id,
                'title': homework.title,
                'description': homework.description,
                'due_date': homework.due_date.strftime('%d/%m/%Y') if homework.due_date else 'Non spécifiée',
                'subject': homework.subject,
                'assigned_by': f"{homework.assigned_by.prenom} {homework.assigned_by.nom}",
                'done_by_student': completion is not None,
                'rubrique': homework.rubrique.nom if homework.rubrique else None
            }
            
            homework_list.append(homework_data)
    
    # Vérifier si la requête vient d'un iframe
    is_iframe = request.args.get('iframe', 'false') == 'true'
    
    # Récupérer les labels pour le titre
    from app.lang.lang_fr import LABELS as labels_fr
    from app.lang.lang_en import LABELS as labels_en
    lang = request.cookies.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    if is_iframe:
        return render_template('todo.html', my_lists=my_lists, shared_lists=shared_lists, 
                              homework_list=homework_list, title=labels.get('todo', 'Todo'))
    else:
        return render_template('todo.html', my_lists=my_lists, shared_lists=shared_lists, 
                              homework_list=homework_list)

@misc_bp.route('/todo/toggle_homework/<int:homework_id>', methods=['POST'])
@login_required
def toggle_homework(homework_id):
    # Vérifier que l'utilisateur est un élève
    if current_user.role != 'eleve':
        flash('Seuls les élèves peuvent marquer les devoirs comme faits')
        return redirect(url_for('misc.todo'))
    
    # Récupérer la classe de l'élève (directement ou via son groupe)
    student_class_id = current_user.class_id
    if student_class_id is None and current_user.group_id is not None:
        # Si l'élève n'a pas de classe directement assignée mais est dans un groupe,
        # récupérer la classe du groupe
        group = Group.query.get(current_user.group_id)
        if group:
            student_class_id = group.class_id
    
    # Vérifier que le devoir existe et est assigné à l'élève
    homework = Homework.query.get_or_404(homework_id)
    if (homework.class_id != student_class_id and 
        homework.group_id != current_user.group_id):
        flash('Ce devoir ne vous est pas assigné')
        return redirect(url_for('misc.todo'))
    
    # Vérifier si l'élève a déjà marqué ce devoir comme fait
    completion = HomeworkCompletion.query.filter_by(
        homework_id=homework_id,
        student_id=current_user.id
    ).first()
    
    if completion:
        # Si le devoir est déjà marqué comme fait, le supprimer
        db.session.delete(completion)
        flash('Devoir marqué comme non fait')
    else:
        # Sinon, créer une nouvelle entrée
        completion = HomeworkCompletion(
            homework_id=homework_id,
            student_id=current_user.id
        )
        db.session.add(completion)
        flash('Devoir marqué comme fait')
    
    db.session.commit()
    
    # Vérifier si la requête vient du dashboard ou de la page todo
    # Si le paramètre 'from_dashboard' est présent, retourner une réponse JSON
    if request.args.get('from_dashboard') == 'true' or request.form.get('from_dashboard') == 'true':
        # Retourner une réponse JSON pour les requêtes AJAX
        from flask import jsonify
        return jsonify({'success': True})
    
    # Sinon, rediriger vers la page todo
    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/add_list', methods=['POST'])
@login_required
def add_todo_list():
    title = request.form.get('title')
    if title:
        new_list = TodoList(title=title, owner_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        flash('Liste créée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/rename_list/<int:list_id>', methods=['POST'])
@login_required
def rename_todo_list(list_id):
    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.owner_id != current_user.id:
        return "Accès non autorisé", 403

    title = request.form.get('title')
    if title:
        todo_list.title = title
        db.session.commit()
        flash('Liste renommée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/delete_list/<int:list_id>', methods=['POST'])
@login_required
def delete_todo_list(list_id):
    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.owner_id != current_user.id:
        return "Accès non autorisé", 403

    db.session.delete(todo_list)
    db.session.commit()
    flash('Liste supprimée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/add_item/<int:list_id>', methods=['POST'])
@login_required
def add_todo_item(list_id):
    todo_list = TodoList.query.get_or_404(list_id)

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    content = request.form.get('content')
    if content:
        item = TodoItem(content=content, list_id=list_id)
        db.session.add(item)
        db.session.commit()
        flash('Tâche ajoutée')

    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/toggle_item/<int:item_id>', methods=['POST'])
@login_required
def toggle_todo_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    item.done = not item.done
    db.session.commit()
    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_todo_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('misc.todo'))

@misc_bp.route('/todo/edit_item/<int:item_id>', methods=['POST'])
@login_required
def edit_todo_item(item_id):
    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    content = request.form.get('content')
    if content:
        item.content = content
        db.session.commit()

    return redirect(url_for('misc.todo'))

# Classes & groupes routes
@misc_bp.route('/classes', methods=['GET', 'POST'])
@login_required
def classes():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'class':
            nom = request.form.get('nom')
            niveau = request.form.get('niveau')
            if nom and niveau:
                new_class = SchoolClass(nom=nom, niveau=niveau)
                db.session.add(new_class)
                db.session.commit()
                flash('Classe créée avec succès')
            else:
                flash('Veuillez remplir tous les champs')
        elif form_type == 'group':
            nom = request.form.get('group_nom')
            class_id = request.form.get('class_id')
            if nom and class_id:
                new_group = Group(nom=nom, class_id=class_id)
                db.session.add(new_group)
                db.session.commit()
                flash('Groupe créé avec succès')
            else:
                flash('Veuillez remplir tous les champs')
        elif form_type == 'add_student_to_group':
            user_id = request.form.get('user_id')
            group_id = request.form.get('group_id')
            if user_id and group_id:
                user = User.query.get(user_id)
                group = Group.query.get(group_id)
                
                # Mettre à jour le groupe de l'élève
                user.group_id = group_id
                
                # Mettre également à jour la classe de l'élève avec la classe du groupe
                if group and group.class_id:
                    user.class_id = group.class_id
                
                db.session.commit()
                flash('Élève ajouté au groupe')
            else:
                flash('Veuillez sélectionner un élève')
        return redirect(url_for('misc.classes', class_id=request.args.get('class_id'), group_id=request.args.get('group_id')))

    class_id = request.args.get('class_id', type=int)
    group_id = request.args.get('group_id', type=int)
    classes = SchoolClass.query.all()
    selected_class = None
    groups = []
    selected_group = None
    group_students = []
    unassigned_students = []
    if class_id:
        selected_class = SchoolClass.query.get(class_id)
        if selected_class:
            groups = Group.query.filter_by(class_id=class_id).all()
            if group_id:
                selected_group = Group.query.get(group_id)
                if selected_group:
                    group_students = selected_group.users
            unassigned_students = User.query.filter_by(group_id=None, role='eleve').all()
    return render_template('classes.html',
                           classes=classes,
                           selected_class=selected_class,
                           groups=groups,
                           selected_group=selected_group,
                           group_students=group_students,
                           unassigned_students=unassigned_students)

@misc_bp.route('/groups/remove_student/<int:user_id>', methods=['POST'])
@login_required
def remove_student_from_group(user_id):
    user = User.query.get_or_404(user_id)
    group = user.group
    
    # Retirer l'élève du groupe
    user.group_id = None
    
    # Retirer également l'élève de la classe si nécessaire
    # (optionnel, selon la logique métier souhaitée)
    user.class_id = None
    
    db.session.commit()
    flash('Élève retiré du groupe')
    return redirect(url_for('misc.classes', class_id=group.class_id, group_id=group.id))

@misc_bp.route('/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    for group in school_class.groups:
        db.session.delete(group)
    db.session.delete(school_class)
    db.session.commit()
    flash('Classe supprimée avec succès')
    return redirect(url_for('misc.classes'))

@misc_bp.route('/groups/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    class_id = group.class_id
    db.session.delete(group)
    db.session.commit()
    flash('Groupe supprimé avec succès')
    return redirect(url_for('misc.classes', class_id=class_id))

@misc_bp.route('/classes/edit/<int:class_id>', methods=['POST'])
@login_required
def edit_class(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    nom = request.form.get('nom')
    niveau = request.form.get('niveau')
    if nom and niveau:
        school_class.nom = nom
        school_class.niveau = niveau
        db.session.commit()
        flash('Classe modifiée avec succès')
    else:
        flash('Veuillez remplir tous les champs')
    return redirect(url_for('misc.classes', class_id=class_id))

@misc_bp.route('/groups/edit/<int:group_id>', methods=['POST'])
@login_required
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)
    nom = request.form.get('nom')
    if nom:
        group.nom = nom
        db.session.commit()
        flash('Groupe modifié avec succès')
    else:
        flash('Veuillez remplir le nom')
    return redirect(url_for('misc.classes', class_id=group.class_id))

# Routes pour la gestion des devoirs
@misc_bp.route('/homework', methods=['GET'])
@login_required
def homework():
    # Vérifier que l'utilisateur est un professeur ou un administrateur
    if current_user.role not in ['professeur', 'admin']:
        flash('Accès non autorisé')
        return redirect(url_for('dashboard.home'))
    
    # Récupérer tous les devoirs
    if current_user.role == 'admin':
        # Les administrateurs voient tous les devoirs
        homework_list = Homework.query.all()
    else:
        # Les professeurs ne voient que leurs propres devoirs
        homework_list = Homework.query.filter_by(assigned_by_id=current_user.id).all()
    
    # Récupérer toutes les classes, tous les groupes et toutes les rubriques pour le formulaire
    classes = SchoolClass.query.all()
    groups = Group.query.all()
    rubriques = Rubrique.query.all()
    
    return render_template('homework.html', 
                          homework_list=homework_list,
                          classes=classes,
                          groups=groups,
                          rubriques=rubriques)

@misc_bp.route('/homework/add', methods=['POST'])
@login_required
def add_homework():
    # Vérifier que l'utilisateur est un professeur ou un administrateur
    if current_user.role not in ['professeur', 'admin']:
        flash('Accès non autorisé')
        return redirect(url_for('dashboard.home'))
    
    # Récupérer les données du formulaire
    title = request.form.get('title')
    description = request.form.get('description')
    subject = request.form.get('subject')
    due_date_str = request.form.get('due_date')
    assignment_type = request.form.get('assignment_type')
    
    # Récupérer les informations de notification
    notification_message = request.form.get('notification_message', '').strip()
    send_notification = 'send_notification' in request.form
    
    # Convertir la date
    from datetime import datetime
    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Format de date invalide')
        return redirect(url_for('misc.homework'))
    
    # Récupérer la rubrique
    rubrique_id = request.form.get('rubrique_id')
    
    # Créer le devoir
    homework = Homework(
        title=title,
        description=description,
        subject=subject,
        due_date=due_date,
        assigned_by_id=current_user.id,
        rubrique_id=rubrique_id if rubrique_id else None
    )
    
    # Assigner à une classe ou un groupe
    class_id = None
    group_id = None
    
    if assignment_type == 'class':
        class_id = request.form.get('class_id')
        if class_id:
            homework.class_id = class_id
    elif assignment_type == 'group':
        group_id = request.form.get('group_id')
        if group_id:
            homework.group_id = group_id
    
    # Sauvegarder le devoir
    db.session.add(homework)
    db.session.commit()
    
    # Envoyer une notification si demandé
    if send_notification and (class_id or group_id):
        # Importer les modèles de messagerie
        from app.models import Message, MessageRecipient
        
        # Créer un message par défaut si aucun message n'est fourni
        if not notification_message:
            due_date_formatted = due_date.strftime('%d/%m/%Y')
            subject_info = f" en {subject}" if subject else ""
            notification_message = f"Un nouveau devoir '{title}'{subject_info} vous a été assigné, à rendre pour le {due_date_formatted}."
        
        # Créer le message
        message = Message(sender_id=current_user.id, content=notification_message)
        db.session.add(message)
        db.session.flush()  # Pour obtenir l'ID du message
        
        # Créer les destinataires
        recipients = []
        
        # Ajouter les destinataires en fonction du type d'assignation
        if class_id:
            # Si assigné à une classe, envoyer à tous les groupes de cette classe
            school_class = SchoolClass.query.get(class_id)
            if school_class:
                groups = school_class.groups
                for group in groups:
                    recipients.append(MessageRecipient(
                        message_id=message.id,
                        recipient_group_id=group.id
                    ))
        elif group_id:
            # Si assigné à un groupe, envoyer directement au groupe
            recipients.append(MessageRecipient(
                message_id=message.id,
                recipient_group_id=int(group_id)
            ))
        
        # Enregistrer les destinataires
        if recipients:
            db.session.add_all(recipients)
            db.session.commit()
            flash('Devoir ajouté et notification envoyée avec succès', 'success')
        else:
            flash('Devoir ajouté avec succès, mais aucune notification n\'a été envoyée (aucun destinataire valide)', 'warning')
    else:
        flash('Devoir ajouté avec succès')
    
    return redirect(url_for('misc.homework'))

@misc_bp.route('/homework/edit/<int:homework_id>', methods=['GET', 'POST'])
@login_required
def edit_homework(homework_id):
    # Vérifier que l'utilisateur est un professeur ou un administrateur
    if current_user.role not in ['professeur', 'admin']:
        flash('Accès non autorisé')
        return redirect(url_for('dashboard.home'))
    
    # Récupérer le devoir
    homework = Homework.query.get_or_404(homework_id)
    
    # Vérifier que l'utilisateur est l'auteur du devoir ou un administrateur
    if homework.assigned_by_id != current_user.id and current_user.role != 'admin':
        flash('Vous ne pouvez pas modifier ce devoir')
        return redirect(url_for('misc.homework'))
    
    if request.method == 'POST':
        # Mettre à jour le devoir
        homework.title = request.form.get('title')
        homework.description = request.form.get('description')
        homework.subject = request.form.get('subject')
        
        # Convertir la date
        due_date_str = request.form.get('due_date')
        try:
            homework.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Format de date invalide')
            return redirect(url_for('misc.edit_homework', homework_id=homework_id))
        
        # Récupérer les informations de notification
        notification_message = request.form.get('notification_message', '').strip()
        send_notification = 'send_notification' in request.form
        
        # Mettre à jour l'assignation
        assignment_type = request.form.get('assignment_type')
        old_class_id = homework.class_id
        old_group_id = homework.group_id
        homework.class_id = None
        homework.group_id = None
        
        class_id = None
        group_id = None
        
        if assignment_type == 'class':
            class_id = request.form.get('class_id')
            if class_id:
                homework.class_id = class_id
        elif assignment_type == 'group':
            group_id = request.form.get('group_id')
            if group_id:
                homework.group_id = group_id
        
        # Sauvegarder les modifications
        db.session.commit()
        
        # Envoyer une notification si demandé
        if send_notification and (class_id or group_id):
            # Importer les modèles de messagerie
            from app.models import Message, MessageRecipient
            
            # Créer un message par défaut si aucun message n'est fourni
            if not notification_message:
                due_date_formatted = homework.due_date.strftime('%d/%m/%Y')
                subject_info = f" en {homework.subject}" if homework.subject else ""
                notification_message = f"Le devoir '{homework.title}'{subject_info} a été modifié, à rendre pour le {due_date_formatted}."
            
            # Créer le message
            message = Message(sender_id=current_user.id, content=notification_message)
            db.session.add(message)
            db.session.flush()  # Pour obtenir l'ID du message
            
            # Créer les destinataires
            recipients = []
            
            # Ajouter les destinataires en fonction du type d'assignation
            if class_id:
                # Si assigné à une classe, envoyer à tous les groupes de cette classe
                school_class = SchoolClass.query.get(class_id)
                if school_class:
                    groups = school_class.groups
                    for group in groups:
                        recipients.append(MessageRecipient(
                            message_id=message.id,
                            recipient_group_id=group.id
                        ))
            elif group_id:
                # Si assigné à un groupe, envoyer directement au groupe
                recipients.append(MessageRecipient(
                    message_id=message.id,
                    recipient_group_id=int(group_id)
                ))
            
            # Enregistrer les destinataires
            if recipients:
                db.session.add_all(recipients)
                db.session.commit()
                flash('Devoir modifié et notification envoyée avec succès', 'success')
            else:
                flash('Devoir modifié avec succès, mais aucune notification n\'a été envoyée (aucun destinataire valide)', 'warning')
        else:
            flash('Devoir modifié avec succès')
        
        return redirect(url_for('misc.homework'))
    
    # Récupérer toutes les classes, tous les groupes et toutes les rubriques pour le formulaire
    classes = SchoolClass.query.all()
    groups = Group.query.all()
    rubriques = Rubrique.query.all()
    
    # Déterminer le type d'assignation actuel
    assignment_type = None
    if homework.class_id:
        assignment_type = 'class'
    elif homework.group_id:
        assignment_type = 'group'
    
    return render_template('edit_homework.html',
                          homework=homework,
                          classes=classes,
                          groups=groups,
                          rubriques=rubriques,
                          assignment_type=assignment_type)

@misc_bp.route('/homework/reuse/<int:homework_id>', methods=['GET'])
@login_required
def reuse_homework(homework_id):
    # Vérifier que l'utilisateur est un professeur ou un administrateur
    if current_user.role not in ['professeur', 'admin']:
        flash('Accès non autorisé')
        return redirect(url_for('dashboard.home'))
    
    # Récupérer le devoir original
    original_homework = Homework.query.get_or_404(homework_id)
    
    # Créer une copie du devoir
    new_homework = Homework(
        title=f"Copie de {original_homework.title}",
        description=original_homework.description,
        subject=original_homework.subject,
        due_date=original_homework.due_date,
        assigned_by_id=current_user.id,
        rubrique_id=original_homework.rubrique_id,
        # Ne pas copier class_id ou group_id pour permettre une nouvelle affectation
    )
    
    # Sauvegarder le nouveau devoir
    db.session.add(new_homework)
    db.session.commit()
    
    flash('Devoir dupliqué avec succès. Vous pouvez maintenant le modifier et l\'assigner à une classe ou un groupe.')
    
    # Rediriger vers le formulaire d'édition du nouveau devoir
    return redirect(url_for('misc.edit_homework', homework_id=new_homework.id))

@misc_bp.route('/homework/delete/<int:homework_id>', methods=['POST'])
@login_required
def delete_homework(homework_id):
    # Vérifier que l'utilisateur est un professeur ou un administrateur
    if current_user.role not in ['professeur', 'admin']:
        flash('Accès non autorisé')
        return redirect(url_for('dashboard.home'))
    
    # Récupérer le devoir
    homework = Homework.query.get_or_404(homework_id)
    
    # Vérifier que l'utilisateur est l'auteur du devoir ou un administrateur
    if homework.assigned_by_id != current_user.id and current_user.role != 'admin':
        flash('Vous ne pouvez pas supprimer ce devoir')
        return redirect(url_for('misc.homework'))
    
    # Supprimer le devoir
    db.session.delete(homework)
    db.session.commit()
    
    flash('Devoir supprimé avec succès')
    return redirect(url_for('misc.homework'))
