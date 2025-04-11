from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from app import db
from app.lang.lang_fr import LABELS as labels_fr
from app.lang.lang_en import LABELS as labels_en
from app.models import Document, DocumentAssignment, ExerciseAssignment, Project, ProjectParticipant
from app.models import Homework, HomeworkCompletion, Message, MessageRecipient, Group, WelcomeMessage
from sqlalchemy import or_
from datetime import datetime, timedelta

eleve_bp = Blueprint('eleve', __name__, url_prefix='/eleve')

@eleve_bp.route('/dashboard')
@login_required
def dashboard():
    lang = session.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en

    # Documents personnels
    personal_docs = Document.query.filter_by(user_id=current_user.id, type='document')

    filters = [DocumentAssignment.user_id == current_user.id]

    if hasattr(current_user, 'group_id') and current_user.group_id is not None:
        filters.append(DocumentAssignment.group_id == current_user.group_id)

    if hasattr(current_user, 'group') and current_user.group and hasattr(current_user.group, 'school_class') and current_user.group.school_class:
        filters.append(DocumentAssignment.class_id == current_user.group.school_class.id)

    assigned_docs = Document.query.join(DocumentAssignment).filter(
        Document.type == 'document',
        or_(*filters)
    )

    docs = personal_docs.union(assigned_docs).all()

    # Exercices personnels
    personal_exs = Document.query.filter_by(user_id=current_user.id, type='exercise')

    filters_ex = [ExerciseAssignment.user_id == current_user.id]

    if hasattr(current_user, 'group_id') and current_user.group_id is not None:
        filters_ex.append(ExerciseAssignment.group_id == current_user.group_id)

    if hasattr(current_user, 'group') and current_user.group and hasattr(current_user.group, 'school_class') and current_user.group.school_class:
        filters_ex.append(ExerciseAssignment.class_id == current_user.group.school_class.id)

    assigned_exs = Document.query.join(ExerciseAssignment).filter(
        Document.type == 'exercise',
        or_(*filters_ex)
    )

    exs = personal_exs.union(assigned_exs).all()

    # Projets
    # Projets dont l'utilisateur est propriétaire
    owned_projects = Project.query.filter_by(owner_id=current_user.id).all()
    
    # Projets auxquels l'utilisateur participe
    participated_projects_ids = db.session.query(ProjectParticipant.project_id).filter_by(user_id=current_user.id).all()
    participated_projects_ids = [id[0] for id in participated_projects_ids]
    participated_projects = Project.query.filter(Project.id.in_(participated_projects_ids)).all()
    
    # Combiner les deux listes de projets
    projects = owned_projects + [p for p in participated_projects if p not in owned_projects]
    
    # Récupérer les devoirs assignés à l'élève
    homework_list = []
    
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
            'done_by_student': completion is not None
        }
        
        homework_list.append(homework_data)
    
    # Récupérer les notifications non lues
    
    # Messages non lus
    unread_messages_count = MessageRecipient.query.filter_by(
        recipient_user_id=current_user.id,
        is_read=False
    ).count()
    
    # Compter les devoirs non complétés par l'élève
    # Récupérer tous les devoirs assignés à l'élève
    homework_to_do_count = 0
    for homework in homework_query.all():
        # Vérifier si l'élève a déjà marqué ce devoir comme fait
        completion = HomeworkCompletion.query.filter_by(
            homework_id=homework.id,
            student_id=current_user.id
        ).first()
        
        # Si le devoir n'est pas marqué comme fait, l'ajouter au compteur
        if completion is None:
            homework_to_do_count += 1
    
    # Projets mis à jour récemment
    # Projets auxquels l'élève participe
    participated_projects_ids = db.session.query(ProjectParticipant.project_id).filter_by(user_id=current_user.id).all()
    participated_projects_ids = [id[0] for id in participated_projects_ids]
    
    # Projets mis à jour dans les 7 derniers jours
    one_week_ago = datetime.now() - timedelta(days=7)
    
    # Vérifier si Project a un attribut updated_at
    if hasattr(Project, 'updated_at'):
        updated_projects = Project.query.filter(
            Project.id.in_(participated_projects_ids),
            Project.updated_at >= one_week_ago
        ).count()
    else:
        # Utiliser created_at si updated_at n'existe pas
        updated_projects = Project.query.filter(
            Project.id.in_(participated_projects_ids),
            Project.created_at >= one_week_ago
        ).count()
    
    notifications = {
        'messages': unread_messages_count,
        'assignments': homework_to_do_count,
        'projects': updated_projects
    }

    return render_template('eleve_base.html', labels=labels, current_user=current_user, 
                          documents=docs, exercises=exs, projects=projects,
                          homework_list=homework_list, notifications=notifications)
