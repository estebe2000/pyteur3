from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from app import db
from app.lang.lang_fr import LABELS as labels_fr
from app.lang.lang_en import LABELS as labels_en
from app.models import Document, DocumentAssignment, ExerciseAssignment, Project, ProjectParticipant
from sqlalchemy import or_

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

    return render_template('eleve_base.html', labels=labels, current_user=current_user, 
                          documents=docs, exercises=exs, projects=projects)
