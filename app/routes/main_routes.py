from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Document, SchoolClass, Group
from app.ia_providers import provider_manager

main_bp = Blueprint('main', __name__)

@main_bp.route('/qcm')
@login_required
def qcm():
    if current_user.role == 'eleve':
        return "Accès non autorisé", 403

    import glob
    import os
    # banques de questions
    base_dir = os.path.join('app', 'static', 'data', 'qcm')
    pattern = os.path.join(base_dir, '**', '*.json')
    files = glob.glob(pattern, recursive=True)
    qcm_files = [os.path.relpath(f, base_dir).replace('\\', '/') for f in files]

    # qcm sauvegardés
    saved_dir = os.path.join('app', 'static', 'uploads', 'qcm')
    saved_pattern = os.path.join(saved_dir, '*.json')
    saved_files = glob.glob(saved_pattern)
    saved_qcms = [os.path.basename(f) for f in saved_files]

    return render_template('qcm.html', qcm_files=qcm_files, saved_qcms=saved_qcms)

@main_bp.route('/statistiques')
@login_required
def statistiques():
    return render_template('statistiques.html')

@main_bp.route('/messagerie')
@login_required
def messagerie():
    return render_template('messagerie.html')

@main_bp.route('/todo', methods=['GET'])
@login_required
def todo():
    from app.models import TodoList, TodoListAssignment

    # Mes listes
    my_lists = TodoList.query.filter_by(owner_id=current_user.id).all()

    # Listes partagées avec moi
    shared_lists = (
        TodoList.query.join(TodoListAssignment)
        .filter(TodoListAssignment.user_id == current_user.id)
        .all()
    )

    return render_template('todo.html', my_lists=my_lists, shared_lists=shared_lists)


@main_bp.route('/todo/add_list', methods=['POST'])
@login_required
def add_todo_list():
    from app.models import TodoList

    title = request.form.get('title')
    if title:
        new_list = TodoList(title=title, owner_id=current_user.id)
        db.session.add(new_list)
        db.session.commit()
        flash('Liste créée')

    return redirect(url_for('main.todo'))


@main_bp.route('/todo/rename_list/<int:list_id>', methods=['POST'])
@login_required
def rename_todo_list(list_id):
    from app.models import TodoList

    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.owner_id != current_user.id:
        return "Accès non autorisé", 403

    title = request.form.get('title')
    if title:
        todo_list.title = title
        db.session.commit()
        flash('Liste renommée')

    return redirect(url_for('main.todo'))


@main_bp.route('/todo/delete_list/<int:list_id>', methods=['POST'])
@login_required
def delete_todo_list(list_id):
    from app.models import TodoList

    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.owner_id != current_user.id:
        return "Accès non autorisé", 403

    db.session.delete(todo_list)
    db.session.commit()
    flash('Liste supprimée')

    return redirect(url_for('main.todo'))


@main_bp.route('/todo/add_item/<int:list_id>', methods=['POST'])
@login_required
def add_todo_item(list_id):
    from app.models import TodoList, TodoItem

    todo_list = TodoList.query.get_or_404(list_id)

    # Vérifier que l'utilisateur est propriétaire ou a accès
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

    return redirect(url_for('main.todo'))


@main_bp.route('/todo/toggle_item/<int:item_id>', methods=['POST'])
@login_required
def toggle_todo_item(item_id):
    from app.models import TodoItem, TodoList

    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    item.done = not item.done
    db.session.commit()
    return redirect(url_for('main.todo'))


@main_bp.route('/todo/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_todo_item(item_id):
    from app.models import TodoItem, TodoList

    item = TodoItem.query.get_or_404(item_id)
    todo_list = item.list

    if todo_list.owner_id != current_user.id and not any(
        assign.user_id == current_user.id for assign in todo_list.assignments
    ):
        return "Accès non autorisé", 403

    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('main.todo'))


@main_bp.route('/todo/edit_item/<int:item_id>', methods=['POST'])
@login_required
def edit_todo_item(item_id):
    from app.models import TodoItem, TodoList

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

    return redirect(url_for('main.todo'))

@main_bp.route('/projets')
@login_required
def projets():
    return render_template('projets.html')

@main_bp.route('/drive')
@login_required
def drive():
    return render_template('drive.html')

@main_bp.route('/')
@login_required
def home():
    import datetime
    nb_eleves = User.query.filter_by(role='eleve').count()
    nb_profs = User.query.filter_by(role='professeur').count()
    nb_classes = SchoolClass.query.count()
    nb_exercices = Document.query.filter_by(type='exercise').count()
    nb_documents = Document.query.filter_by(type='document').count()
    return render_template('dashboard.html',
                           user=current_user,
                           now=datetime.datetime.now(),
                           nb_eleves=nb_eleves,
                           nb_profs=nb_profs,
                           nb_classes=nb_classes,
                           nb_exercices=nb_exercices,
                           nb_documents=nb_documents)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login')
        password = request.form.get('password')
        
        user = User.query.filter_by(login=login_input).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        
        flash('Login ou mot de passe incorrect.')
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/documents')
@login_required
def documents():
    from app.models import DocumentAssignment
    from sqlalchemy import or_

    # Documents personnels
    personal_docs = Document.query.filter_by(user_id=current_user.id, type='document')

    # Construction dynamique du filtre
    filters = [DocumentAssignment.user_id == current_user.id]

    if current_user.group_id is not None:
        filters.append(DocumentAssignment.group_id == current_user.group_id)

    if current_user.group and current_user.group.school_class:
        filters.append(DocumentAssignment.class_id == current_user.group.school_class.id)

    # Documents affectés
    assigned_docs = Document.query.join(DocumentAssignment).filter(
        Document.type == 'document',
        or_(*filters)
    )

    # Union sans doublons
    docs = personal_docs.union(assigned_docs).all()

    return render_template('documents.html', documents=docs)

@main_bp.route('/exercises')
@login_required
def exercises():
    print("DEBUG - current_user.id:", current_user.id)
    print("DEBUG - current_user.group_id:", current_user.group_id)
    print("DEBUG - current_user.class_id:", current_user.class_id)
    from app.models import ExerciseAssignment
    from sqlalchemy import or_

    # Exercices personnels
    personal_exercises = Document.query.filter_by(user_id=current_user.id, type='exercise')

    # Construction dynamique du filtre
    filters = [ExerciseAssignment.user_id == current_user.id]

    if current_user.group_id is not None:
        filters.append(ExerciseAssignment.group_id == current_user.group_id)

    if current_user.group and current_user.group.school_class:
        filters.append(ExerciseAssignment.class_id == current_user.group.school_class.id)

    # Exercices affectés
    assigned_exercises = Document.query.join(ExerciseAssignment).filter(
        Document.type == 'exercise',
        or_(*filters)
    )

    # Union sans doublons
    exercises = personal_exercises.union(assigned_exercises).all()

    return render_template('exercises.html', exercises=exercises)

@main_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{filename}"

        upload_folder = os.path.join('app', 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        file.save(os.path.join(upload_folder, unique_filename))
        
        new_doc = Document(
            filename=unique_filename,
            original_filename=filename,
            tags=request.form.get('tags', ''),
            user_id=current_user.id,
            type='document'
        )
        db.session.add(new_doc)
        db.session.commit()
        
        flash('Document uploadé avec succès')
        return redirect(url_for('main.documents'))
    
    flash('Type de fichier non autorisé (PDF uniquement)')
    return redirect(url_for('main.documents'))

@main_bp.route('/upload_exercise', methods=['POST'])
@login_required
def upload_exercise():
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(request.url)
    
    allowed_exercise_ext = {'py', 'sql', 'js', 'ml', 'xcas'}
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_exercise_ext:
        filename = secure_filename(file.filename)
        unique_filename = f"{current_user.id}_{filename}"

        upload_folder = os.path.join('app', 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        file.save(os.path.join(upload_folder, unique_filename))
        
        new_ex = Document(
            filename=unique_filename,
            original_filename=filename,
            tags=request.form.get('tags', ''),
            user_id=current_user.id,
            type='exercise'
        )
        db.session.add(new_ex)
        db.session.commit()
        
        flash('Exercice uploadé avec succès')
        return redirect(url_for('main.exercises'))
    
    flash('Type de fichier non autorisé (py, sql, js, ml, xcas uniquement)')
    return redirect(url_for('main.exercises'))

from app import csrf
import csv
import datetime
from werkzeug.security import generate_password_hash
from flask import send_from_directory


@main_bp.route('/assign_document/<int:document_id>', methods=['GET', 'POST'])
@login_required
def assign_document(document_id):
    if current_user.role != 'admin':
        return "Accès non autorisé", 403

    from app.models import User, Group, SchoolClass, DocumentAssignment, Document

    document = Document.query.get_or_404(document_id)

    if request.method == 'POST':
        # Supprimer les affectations existantes
        DocumentAssignment.query.filter_by(document_id=document_id).delete()

        # Affectation aux élèves
        user_ids = request.form.getlist('users')
        for uid in user_ids:
            assign = DocumentAssignment(document_id=document_id, user_id=int(uid))
            db.session.add(assign)

        # Affectation aux groupes
        group_ids = request.form.getlist('groups')
        for gid in group_ids:
            assign = DocumentAssignment(document_id=document_id, group_id=int(gid))
            db.session.add(assign)

        # Affectation aux classes
        class_ids = request.form.getlist('classes')
        for cid in class_ids:
            assign = DocumentAssignment(document_id=document_id, class_id=int(cid))
            db.session.add(assign)

        db.session.commit()
        flash("Affectations mises à jour")
        return redirect(url_for('main.documents'))

    # GET : afficher formulaire
    users = User.query.filter_by(role='eleve').all()
    groups = Group.query.all()
    classes = SchoolClass.query.all()

    # Affectations existantes
    existing = DocumentAssignment.query.filter_by(document_id=document_id).all()
    assigned_users = [a.user_id for a in existing if a.user_id]
    assigned_groups = [a.group_id for a in existing if a.group_id]
    assigned_classes = [a.class_id for a in existing if a.class_id]

    return render_template('assign_exercise.html',
                           exercise=document,
                           users=users,
                           groups=groups,
                           classes=classes,
                           assigned_users=assigned_users,
                           assigned_groups=assigned_groups,
                           assigned_classes=assigned_classes)

@main_bp.route('/assign_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def assign_exercise(exercise_id):
    if current_user.role != 'admin':
        return "Accès non autorisé", 403

    from app.models import User, Group, SchoolClass, ExerciseAssignment, Document

    exercise = Document.query.get_or_404(exercise_id)

    if request.method == 'POST':
        # Supprimer les affectations existantes
        ExerciseAssignment.query.filter_by(exercise_id=exercise_id).delete()

        # Affectation aux élèves
        user_ids = request.form.getlist('users')
        for uid in user_ids:
            assign = ExerciseAssignment(exercise_id=exercise_id, user_id=int(uid))
            db.session.add(assign)

        # Affectation aux groupes
        group_ids = request.form.getlist('groups')
        for gid in group_ids:
            assign = ExerciseAssignment(exercise_id=exercise_id, group_id=int(gid))
            db.session.add(assign)

        # Affectation aux classes
        class_ids = request.form.getlist('classes')
        for cid in class_ids:
            assign = ExerciseAssignment(exercise_id=exercise_id, class_id=int(cid))
            db.session.add(assign)

        db.session.commit()
        flash("Affectations mises à jour")
        return redirect(url_for('main.exercises'))

    # GET : afficher formulaire
    users = User.query.filter_by(role='eleve').all()
    groups = Group.query.all()
    classes = SchoolClass.query.all()

    # Affectations existantes
    existing = ExerciseAssignment.query.filter_by(exercise_id=exercise_id).all()
    assigned_users = [a.user_id for a in existing if a.user_id]
    assigned_groups = [a.group_id for a in existing if a.group_id]
    assigned_classes = [a.class_id for a in existing if a.class_id]

    return render_template('assign_exercise.html',
                           exercise=exercise,
                           users=users,
                           groups=groups,
                           classes=classes,
                           assigned_users=assigned_users,
                           assigned_groups=assigned_groups,
                           assigned_classes=assigned_classes)

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.nom = request.form.get('nom')
        current_user.prenom = request.form.get('prenom')
        current_user.login = request.form.get('login')
        current_user.email = request.form.get('email')
        current_user.date_naissance = request.form.get('date_naissance')
        current_user.besoins_particuliers = request.form.get('besoins_particuliers')
        password = request.form.get('password')
        if password:
            from werkzeug.security import generate_password_hash
            current_user.password = generate_password_hash(password)
        db.session.commit()
        flash('Profil mis à jour avec succès.')
    return render_template('settings.html', user=current_user)

@csrf.exempt
@main_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    # if doc.user_id != current_user.id and current_user.role != 'admin':
    #     return "Unauthorized", 403
    
    try:
        os.remove(os.path.join('app', 'static', 'uploads', doc.filename))
        db.session.delete(doc)
        db.session.commit()
        return '', 204
    except Exception as e:
        return str(e), 500


@csrf.exempt
@main_bp.route('/export_pronote', methods=['POST'])
@login_required
def export_pronote():
    import json
    from flask import Response
    try:
        data = request.get_json(force=True)
        qcm_name = data.get('name', 'qcm_export')
        questions = data.get('questions', [])

        # Construction XML Pronote
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n'

        # Catégorie par défaut
        xml += '  <question type="category">\n'
        xml += '    <category>\n'
        xml += f'      <text><![CDATA[<infos><name>{qcm_name}</name><answernumbering>123</answernumbering><niveau>2NDE</niveau><matiere>SC.NUMERIQ.TECHNOL.</matiere></infos>]]></text>\n'
        xml += '    </category>\n'
        xml += '  </question>\n'

        for q in questions:
            question_text = q.get('question', '').replace('&', '&').replace('<', '<').replace('>', '>')
            propositions = q.get('propositions', [])
            bonne_reponse = q.get('bonne_reponse', 0)

            xml += '  <question type="multichoice">\n'
            xml += '    <name>\n'
            xml += f'      <text><![CDATA[{question_text}]]></text>\n'
            xml += '    </name>\n'
            xml += '    <questiontext format="html">\n'
            xml += '      <text><![CDATA[]]></text>\n'
            xml += '    </questiontext>\n'
            xml += '    <externallink/>\n'
            xml += '    <usecase>1</usecase>\n'
            xml += '    <defaultgrade>1</defaultgrade>\n'
            xml += '    <editeur>0</editeur>\n'
            xml += '    <single>true</single>\n'

            for idx, prop in enumerate(propositions):
                prop_text = prop.replace('&', '&').replace('<', '<').replace('>', '>')
                fraction = "100" if idx == bonne_reponse else "0"
                xml += f'    <answer fraction="{fraction}" format="plain_text">\n'
                xml += f'      <text><![CDATA[{prop_text}]]></text>\n'
                xml += '      <feedback>\n'
                xml += '        <text><![CDATA[]]></text>\n'
                xml += '      </feedback>\n'
                xml += '    </answer>\n'

            xml += '  </question>\n'

        xml += '</quiz>\n'

        return Response(
            xml,
            mimetype='application/xml',
            headers={
                'Content-Disposition': f'attachment; filename={qcm_name}.xml'
            }
        )
    except Exception as e:
        return str(e), 500

@csrf.exempt
@main_bp.route('/delete_exercise/<int:ex_id>', methods=['POST'])
@login_required
def delete_exercise(ex_id):
    ex = Document.query.get_or_404(ex_id)
    if ex.user_id != current_user.id and current_user.role != 'admin':
        return "Unauthorized", 403
    
    try:
        os.remove(os.path.join('app', 'static', 'uploads', ex.filename))
        db.session.delete(ex)
        db.session.commit()
        return '', 204
    except Exception as e:
        return str(e), 500

@main_bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    eleves = User.query.filter_by(role='eleve').order_by(User.nom).all()
    profs = User.query.filter_by(role='professeur').order_by(User.nom).all()
    admins = User.query.filter_by(role='admin').order_by(User.nom).all()
    return render_template('users.html', eleves=eleves, profs=profs, admins=admins)

@main_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
        
    if request.method == 'POST':
        import secrets
        import datetime
        password = secrets.token_urlsafe(8)

        date_str = request.form.get('date_naissance')
        if date_str:
            try:
                date_naissance = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                date_naissance = None
        else:
            date_naissance = None
        
        user = User(
            nom=request.form.get('nom'),
            prenom=request.form.get('prenom'),
            login=request.form.get('login'),
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            date_naissance=date_naissance,
            besoins_particuliers=request.form.get('besoins_particuliers'),
            email=request.form.get('email'),
            role=request.form.get('role')
        )
        db.session.add(user)
        db.session.commit()
        
        flash("Utilisateur créé avec succès. Le mot de passe a été envoyé par email.")
        return redirect(url_for('main.users'))
    
    return render_template('add_user.html')

@main_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
        
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.nom = request.form.get('nom')
        user.prenom = request.form.get('prenom') 
        user.login = request.form.get('login')

        date_str = request.form.get('date_naissance')
        if date_str:
            try:
                import datetime
                user.date_naissance = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                user.date_naissance = None
        else:
            user.date_naissance = None

        # Gestion mot de passe
        password = request.form.get('password')
        if password:
            from werkzeug.security import generate_password_hash
            user.password = generate_password_hash(password)

        user.besoins_particuliers = request.form.get('besoins_particuliers')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        
        db.session.commit()
        flash("Utilisateur mis à jour avec succès")
        return redirect(url_for('main.users'))
        
    return render_template('edit_user.html', user=user)

@main_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required 
def delete_user(id):
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé avec succès")
    return redirect(url_for('main.users'))

@main_bp.route('/sandbox')
@login_required
def sandbox():
    return render_template('sandbox.html')

@main_bp.route('/ia')
@login_required
def ia():
    return render_template('ia.html')

@main_bp.route('/groups/remove_student/<int:user_id>', methods=['POST'])
@login_required
def remove_student_from_group(user_id):
    user = User.query.get_or_404(user_id)
    group = user.group
    user.group_id = None
    db.session.commit()
    flash('Élève retiré du groupe')
    return redirect(url_for('main.classes', class_id=group.class_id, group_id=group.id))

@main_bp.route('/classes/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    school_class = SchoolClass.query.get_or_404(class_id)
    for group in school_class.groups:
        db.session.delete(group)
    db.session.delete(school_class)
    db.session.commit()
    flash('Classe supprimée avec succès')
    return redirect(url_for('main.classes'))

@main_bp.route('/groups/delete/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    class_id = group.class_id
    db.session.delete(group)
    db.session.commit()
    flash('Groupe supprimé avec succès')
    return redirect(url_for('main.classes', class_id=class_id))

@main_bp.route('/classes/edit/<int:class_id>', methods=['POST'])
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
    return redirect(url_for('main.classes', class_id=class_id))

@main_bp.route('/groups/edit/<int:group_id>', methods=['POST'])
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
    return redirect(url_for('main.classes', class_id=group.class_id))

@main_bp.route('/classes', methods=['GET', 'POST'])
@login_required
def classes():
    from app.models import User, Group
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
                from app.models import User, Group
                user = User.query.get(user_id)
                user.group_id = group_id
                db.session.commit()
                flash('Élève ajouté au groupe')
            else:
                flash('Veuillez sélectionner un élève')
        return redirect(url_for('main.classes', class_id=request.args.get('class_id'), group_id=request.args.get('group_id')))

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}


from flask import session, request

@main_bp.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in ['fr', 'en']:
        session['lang'] = lang_code
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('main.home'))


from flask import jsonify

from app import csrf

@main_bp.route('/users/import', methods=['GET', 'POST'])
@login_required
def import_users():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403

    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join('app', 'static', 'uploads', filename)
        file.save(filepath)

        # Extraire classe et groupe du nom de fichier, ex: 201.p1.csv
        base = os.path.basename(filename)
        parts = base.split('.')
        classe_nom = parts[0]
        groupe_nom = parts[1] if len(parts) > 1 else 'default'

        # Chercher ou créer la classe
        school_class = SchoolClass.query.filter_by(nom=classe_nom).first()
        if not school_class:
            school_class = SchoolClass(nom=classe_nom, niveau='Inconnu')
            db.session.add(school_class)
            db.session.commit()

        # Chercher ou créer le groupe
        group = Group.query.filter_by(nom=groupe_nom, class_id=school_class.id).first()
        if not group:
            group = Group(nom=groupe_nom, class_id=school_class.id)
            db.session.add(group)
            db.session.commit()

        with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            headers = next(reader, None)  # sauter l'en-tête
            for row in reader:
                if not row or not row[0].strip():
                    continue
                nom_prenom = row[0].strip()
                try:
                    nom_complet = nom_prenom.split(' ')
                    prenom = nom_complet[0]
                    nom = ' '.join(nom_complet[1:])
                except:
                    prenom = nom_prenom
                    nom = ''

                date_naissance_str = row[2].strip() if len(row) > 2 else ''
                try:
                    date_naissance = datetime.datetime.strptime(date_naissance_str, '%d/%m/%Y').date()
                    password_plain = date_naissance.strftime('%d%m%Y')
                except:
                    date_naissance = None
                    password_plain = 'changeme'

                password_hash = generate_password_hash(password_plain)

                # Générer un login unique
                base_login = prenom.lower() + '.' + nom.lower().replace(' ', '')
                login_candidate = base_login
                suffix = 1
                while User.query.filter_by(login=login_candidate).first() is not None:
                    login_candidate = f"{base_login}{suffix}"
                    suffix += 1

                user = User(
                    nom=nom,
                    prenom=prenom,
                    login=login_candidate,
                    password=password_hash,
                    date_naissance=date_naissance,
                    sexe=row[3].strip() if len(row) > 3 else '',
                    besoins_particuliers='',
                    email=None,
                    role='eleve',
                    date_entree=datetime.datetime.strptime(row[5], '%d/%m/%Y').date() if len(row) > 5 and row[5].strip() else None,
                    date_sortie=datetime.datetime.strptime(row[6], '%d/%m/%Y').date() if len(row) > 6 and row[6].strip() else None,
                    tuteur=row[7].strip() if len(row) > 7 else '',
                    connexion_eleve=row[8].strip() if len(row) > 8 else '',
                    connexion_responsable=row[9].strip() if len(row) > 9 else '',
                    option1=row[10].strip() if len(row) > 10 else '',
                    option2=row[11].strip() if len(row) > 11 else '',
                    option3=row[12].strip() if len(row) > 12 else '',
                    autres_options=row[13].strip() if len(row) > 13 else '',
                    regime=row[14].strip() if len(row) > 14 else '',
                    class_id=school_class.id,
                    group_id=group.id
                )
                db.session.add(user)
            db.session.commit()
        flash('Importation terminée avec succès')
        return redirect(url_for('main.users'))

    return render_template('import_users.html')



@csrf.exempt
@main_bp.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({'error': f'Erreur parsing JSON: {str(e)}'}), 400

    if data is None:
        return jsonify({'error': 'Requête JSON invalide ou en-tête Content-Type manquant'}), 400

    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({'error': 'Message vide'}), 400

    try:
        from app.ia_client import generate_text
        ai_response = generate_text(user_message)
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@csrf.exempt
@main_bp.route('/save_qcm', methods=['POST'])
@login_required
def save_qcm():
    import json
    try:
        data = request.get_json(force=True)
        qcm_name = data.get('name', '').strip()
        questions = data.get('questions', [])
        if not qcm_name or not questions:
            return 'Nom ou questions manquants', 400

        save_dir = os.path.join('app', 'static', 'uploads', 'qcm')
        os.makedirs(save_dir, exist_ok=True)
        filename = secure_filename(qcm_name) + '.json'
        filepath = os.path.join(save_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        return '', 200
    except Exception as e:
        return str(e), 500


@main_bp.route('/manage_providers')
@login_required
def manage_providers():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    import json
    try:
        with open('app/ia_providers.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        config_json = json.dumps(config, indent=4, ensure_ascii=False)
    except Exception as e:
        config_json = f"Erreur chargement config: {str(e)}"
    return render_template('manage_providers.html', config_json=config_json)


from flask import jsonify

@main_bp.route('/api/ia_providers', methods=['GET'])
@login_required
def api_list_providers():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import json
    try:
        with open('app/ia_providers.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/ia_providers', methods=['POST'])
@login_required
def api_add_provider():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import json
    data = request.get_json()
    name = data.get('name')
    params = data.get('params')
    if not name or not params:
        return jsonify({'error': 'Nom ou paramètres manquants'}), 400
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name in config['providers']:
                return jsonify({'error': 'Nom déjà utilisé'}), 400
            config['providers'][name] = params
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/ia_providers/<name>', methods=['PUT'])
@login_required
def api_update_provider(name):
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import json
    data = request.get_json()
    params = data.get('params')
    if not params:
        return jsonify({'error': 'Paramètres manquants'}), 400
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name not in config['providers']:
                return jsonify({'error': 'Fournisseur inexistant'}), 404
            config['providers'][name] = params
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/ia_providers/<name>', methods=['DELETE'])
@login_required
def api_delete_provider(name):
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import json
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name not in config['providers']:
                return jsonify({'error': 'Fournisseur inexistant'}), 404
            del config['providers'][name]
            # Si on supprime le fournisseur actif, désactiver
            if config.get('active_provider') == name:
                config['active_provider'] = None
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/ia_providers/activate/<name>', methods=['POST'])
@login_required
def api_activate_provider(name):
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import json
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name not in config['providers']:
                return jsonify({'error': 'Fournisseur inexistant'}), 404
            config['active_provider'] = name
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/ollama_models', methods=['GET'])
@login_required
def api_ollama_models():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import requests, json, os
    try:
        url = 'http://localhost:11434'
        if os.path.exists('app/ia_config.json'):
            with open('app/ia_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config.get('ollama', {}).get('url', url)
        response = requests.get(url.rstrip('/') + '/v1/models', timeout=5)
        if response.status_code != 200:
            return jsonify({'error': f'Status {response.status_code}'}), 500
        data = response.json()
        models = [m['id'] for m in data.get('data', [])]
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/ollama_status', methods=['GET'])
@login_required
def api_ollama_status():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import requests, json, os
    try:
        url = 'http://localhost:11434'
        if os.path.exists('app/ia_config.json'):
            with open('app/ia_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config.get('ollama', {}).get('url', url)
        response = requests.get(url.rstrip('/') + '/v1/models', timeout=3)
        if response.status_code != 200:
            return jsonify({'installed': False, 'models': []})
        data = response.json()
        models = [m['id'] for m in data.get('data', [])]
        return jsonify({'installed': True, 'models': models})
    except Exception:
        return jsonify({'installed': False, 'models': []})


@main_bp.route('/api/ollama_pull', methods=['POST'])
@login_required
def api_ollama_pull():
    if current_user.role != 'admin':
        return {'error': 'Accès refusé'}, 403
    try:
        data = request.get_json(force=True)
        model_name = data.get('model_name')
        if not model_name:
            return {'error': 'Nom du modèle manquant'}, 400
        from app.ollama_api import pull_model
        pull_model(model_name)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}, 500


@main_bp.route('/api/save_ia_config', methods=['POST'])
@login_required
def api_save_ia_config():

    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    import json
    print("DEBUG Headers:", dict(request.headers))
    print("DEBUG Raw data:", request.data)
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("DEBUG JSON parse error:", e)
        return jsonify({'error': 'JSON parse error'}), 400
    print("DEBUG Parsed JSON:", data)
    if not isinstance(data, dict) or not data:
        return jsonify({'error': 'JSON vide ou invalide'}), 400
    try:
        # Charger config existante
        if os.path.exists('app/ia_config.json'):
            with open('app/ia_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}

        # Fusion profonde
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and isinstance(d.get(k), dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v

        deep_update(config, data)

        # Sauvegarder
        with open('app/ia_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/createur_exercice', methods=['GET', 'POST'])
@login_required
def createur_exercice():
    import json
    data_file = 'app/static/data/data.json'
    if request.method == 'POST':
        try:
            new_data = request.form.get('json_data')
            parsed = json.loads(new_data)
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            flash('Données enregistrées avec succès.')
        except Exception as e:
            flash(f'Erreur lors de la sauvegarde: {e}')
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
    return render_template('createur_exercice.html', data_json=json.dumps(data, ensure_ascii=False, indent=2))


@main_bp.route('/generateur_exercice')
@login_required
def generateur_exercice():
    from app.ia_providers import provider_manager
    ia_name = provider_manager.active_provider_name or "Aucun fournisseur"
    model_name = provider_manager.active_provider.model if provider_manager.active_provider else "Aucun modèle"
    return render_template('generateur_exercice.html', ia_name=ia_name, model_name=model_name)


@main_bp.route('/exercices_flash')
@login_required
def exercices_flash():
    from app.ia_providers import provider_manager
    ia_name = provider_manager.active_provider_name or "Aucun fournisseur"
    model_name = provider_manager.active_provider.model if provider_manager.active_provider else "Aucun modèle"
    return render_template('exercices_flash.html', ia_name=ia_name, model_name=model_name)


from flask import jsonify

@main_bp.route('/api/generateur_data', methods=['GET'])
@login_required
def api_generateur_data():
    import json
    try:
        with open('app/static/data/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


from app import csrf

@csrf.exempt
@main_bp.route('/api/generer_exercice', methods=['POST'])
@login_required
def api_generer_exercice():
    import json
    from flask import request
    from app.prompts_generateur import prompt_generation_exercice
    try:
        data = request.get_json(force=True)
        niveau = data.get('niveau')
        theme = data.get('theme')
        difficulte = data.get('difficulte')
        description = data.get('description')
        debutant_str = data.get('debutant', False)
        if isinstance(debutant_str, str):
            debutant = debutant_str.lower() == "true"
        else:
            debutant = bool(debutant_str)

        if not all([niveau, theme, difficulte, description]):
            return jsonify({'error': 'Paramètres manquants'}), 400

        prompt = prompt_generation_exercice(niveau, theme, difficulte, description, debutant=debutant)

        from app.ia_client import generate_text
        reponse = generate_text(prompt)

        return jsonify({'prompt': prompt, 'response': reponse})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@csrf.exempt
@main_bp.route('/api/upload_notebook', methods=['POST'])
@login_required
def api_upload_notebook():
    import os, json
    try:
        data = json.loads(request.data)
        notebook_json = json.dumps(data, ensure_ascii=False, indent=2)

        upload_folder = os.path.join('app', 'static', 'uploads', 'temp')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)

        save_path = os.path.join(upload_folder, '1_programme_nsi_terminal.ipynb')
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(notebook_json)

        return {'success': True}, 200
    except Exception as e:
        return {'error': str(e)}, 500


from flask import jsonify
from app.models import Message, MessageRecipient, User, Group, SchoolClass


from app import csrf

@csrf.exempt
@main_bp.route('/api/messages/delete/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender_id != current_user.id:
        return {'error': 'Non autorisé'}, 403

    # Supprimer les destinataires liés
    MessageRecipient.query.filter_by(message_id=message_id).delete()
    db.session.delete(message)
    db.session.commit()
    return {'success': True}


@csrf.exempt
@main_bp.route('/api/messages/mark_read', methods=['POST'])
@login_required
def mark_message_read():
    try:
        data = request.get_json(force=True)
        message_id = data.get('message_id')
        if not message_id:
            return {'error': 'ID manquant'}, 400

        mr = MessageRecipient.query.filter_by(message_id=message_id, recipient_user_id=current_user.id).first()
        if not mr:
            return {'error': 'Message non trouvé'}, 404

        mr.is_read = True
        db.session.commit()
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}, 500


@csrf.exempt
@main_bp.route('/api/messages/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json(force=True)
    content = data.get('content', '').strip()
    recipient_user_id = data.get('recipient_user_id')
    recipient_group_id = data.get('recipient_group_id')
    recipient_class_id = data.get('recipient_class_id')

    if not content:
        return jsonify({'error': 'Message vide'}), 400

    # Créer le message
    message = Message(sender_id=current_user.id, content=content)
    db.session.add(message)
    db.session.flush()  # pour récupérer message.id

    recipients = []

    # Destinataire individuel
    if recipient_user_id:
        user = User.query.get(recipient_user_id)
        if user:
            recipients.append(MessageRecipient(message_id=message.id, recipient_user_id=user.id))

    # Destinataire groupe
    if recipient_group_id:
        group = Group.query.get(recipient_group_id)
        if group:
            recipients.append(MessageRecipient(message_id=message.id, recipient_group_id=group.id))

    # Destinataire classe (tous les groupes de la classe)
    if recipient_class_id:
        school_class = SchoolClass.query.get(recipient_class_id)
        if school_class:
            groups = school_class.groups
            for group in groups:
                recipients.append(MessageRecipient(message_id=message.id, recipient_group_id=group.id))

    if not recipients:
        return jsonify({'error': 'Aucun destinataire valide'}), 400

    db.session.add_all(recipients)
    db.session.commit()

    return jsonify({'success': True})


@main_bp.route('/api/recipients', methods=['GET'])
@login_required
def get_recipients():
    users = User.query.filter(User.id != current_user.id).all()
    groups = Group.query.all()
    classes = SchoolClass.query.all()

    return jsonify({
        "users": [{"id": u.id, "name": f"{u.prenom} {u.nom}"} for u in users],
        "groups": [{"id": g.id, "name": g.nom} for g in groups],
        "classes": [{"id": c.id, "name": c.nom} for c in classes]
    })


@csrf.exempt
@main_bp.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    # Messages reçus
    direct_msgs = MessageRecipient.query.filter_by(recipient_user_id=current_user.id).all()

    group_msgs = []
    if current_user.group_id:
        group_msgs = MessageRecipient.query.filter_by(recipient_group_id=current_user.group_id).all()

    class_msgs = []
    if current_user.group and current_user.group.school_class:
        class_groups = current_user.group.school_class.groups
        group_ids = [g.id for g in class_groups]
        if group_ids:
            class_msgs = MessageRecipient.query.filter(MessageRecipient.recipient_group_id.in_(group_ids)).all()

    all_recipient_msgs = direct_msgs + group_msgs + class_msgs

    # Supprimer doublons
    unique_recipient_msgs = {}
    for mr in all_recipient_msgs:
        unique_recipient_msgs[mr.message_id] = mr

    # Messages envoyés
    sent_msgs = Message.query.filter_by(sender_id=current_user.id).all()

    messages = []

    # Ajouter messages reçus
    for mr in unique_recipient_msgs.values():
        messages.append({
            'id': mr.message.id,
            'content': mr.message.content,
            'sender_id': mr.message.sender_id,
            'sender_name': f"{mr.message.sender.prenom} {mr.message.sender.nom}",
            'timestamp': mr.message.timestamp.isoformat(),
            'is_read': mr.is_read,
            'sent': False
        })

    # Ajouter messages envoyés
    for m in sent_msgs:
        messages.append({
            'id': m.id,
            'content': m.content,
            'sender_id': m.sender_id,
            'sender_name': f"{current_user.prenom} {current_user.nom}",
            'timestamp': m.timestamp.isoformat(),
            'is_read': True,
            'sent': True
        })

    # Trier par date
    messages.sort(key=lambda m: m['timestamp'])

    return jsonify(messages)
