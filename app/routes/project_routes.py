from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models import Project, ProjectParticipant, User
from app.lang.lang_fr import LABELS as labels_fr
from app.lang.lang_en import LABELS as labels_en
from sqlalchemy import or_
from functools import wraps

project_bp = Blueprint('project', __name__, url_prefix='/project')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin' and current_user.role != 'professeur':
            flash('Accès non autorisé.', 'danger')
            return redirect(url_for('dashboard.home'))
        return f(*args, **kwargs)
    return decorated_function

@project_bp.route('/')
@login_required
def index():
    """Affiche la liste des projets"""
    lang = session.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    # Pour les administrateurs et professeurs, afficher tous les projets
    if current_user.role in ['admin', 'professeur']:
        projects = Project.query.all()
    else:
        # Pour les élèves, afficher uniquement leurs projets
        owned_projects = Project.query.filter_by(owner_id=current_user.id).all()
        
        # Projets auxquels l'élève participe
        participated_projects_ids = db.session.query(ProjectParticipant.project_id).filter_by(user_id=current_user.id).all()
        participated_projects_ids = [id[0] for id in participated_projects_ids]
        participated_projects = Project.query.filter(Project.id.in_(participated_projects_ids)).all()
        
        # Combiner les deux listes
        projects = owned_projects + [p for p in participated_projects if p not in owned_projects]
    
    users = User.query.all()
    
    # Vérifier si la requête vient d'un iframe
    is_iframe = request.args.get('iframe', 'false') == 'true'
    
    # Si c'est un iframe, utiliser un template spécifique
    if is_iframe:
        return render_template('projets.html', projects=projects, users=users, labels=labels, title=labels['projets'])
    else:
        return render_template('projets.html', projects=projects, users=users, labels=labels)

@project_bp.route('/create', methods=['POST'])
@login_required
def create_project():
    """Crée un nouveau projet"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Le titre est obligatoire.', 'danger')
            return redirect(url_for('project.index'))
        
        # Créer le projet
        new_project = Project(
            title=title,
            description=description,
            owner_id=current_user.id
        )
        db.session.add(new_project)
        db.session.flush()  # Pour obtenir l'ID du projet
        
        # Ajouter le propriétaire comme participant
        owner_participant = ProjectParticipant(
            project_id=new_project.id,
            user_id=current_user.id,
            role='owner'
        )
        db.session.add(owner_participant)
        
        # Ajouter les participants sélectionnés
        participants = request.form.getlist('participants')
        for participant_id in participants:
            if participant_id and participant_id.isdigit():
                participant = ProjectParticipant(
                    project_id=new_project.id,
                    user_id=int(participant_id),
                    role='member'
                )
                db.session.add(participant)
        
        db.session.commit()
        flash('Projet créé avec succès.', 'success')
        return redirect(url_for('project.index'))
    
    return redirect(url_for('project.index'))

@project_bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Édite un projet existant"""
    project = Project.query.get_or_404(project_id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if project.owner_id != current_user.id and current_user.role not in ['admin', 'professeur']:
        flash('Vous n\'êtes pas autorisé à modifier ce projet.', 'danger')
        return redirect(url_for('project.index'))
    
    lang = session.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Le titre est obligatoire.', 'danger')
            return redirect(url_for('project.edit_project', project_id=project.id))
        
        project.title = title
        project.description = description
        
        # Mettre à jour les participants
        # D'abord, supprimer tous les participants actuels sauf le propriétaire
        ProjectParticipant.query.filter(
            ProjectParticipant.project_id == project.id,
            ProjectParticipant.role != 'owner'
        ).delete()
        
        # Ensuite, ajouter les nouveaux participants
        participants = request.form.getlist('participants')
        for participant_id in participants:
            if participant_id and participant_id.isdigit():
                participant_id = int(participant_id)
                # Vérifier que l'utilisateur n'est pas déjà le propriétaire
                if participant_id != project.owner_id:
                    participant = ProjectParticipant(
                        project_id=project.id,
                        user_id=participant_id,
                        role='member'
                    )
                    db.session.add(participant)
        
        db.session.commit()
        flash('Projet mis à jour avec succès.', 'success')
        return redirect(url_for('project.index'))
    
    # Récupérer tous les utilisateurs pour le formulaire
    users = User.query.all()
    
    # Récupérer les IDs des participants actuels
    current_participants = [p.user_id for p in project.participants if p.role == 'member']
    
    return render_template('edit_project.html', project=project, users=users, 
                          current_participants=current_participants, labels=labels)

@project_bp.route('/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    """Supprime un projet"""
    project = Project.query.get_or_404(project_id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if project.owner_id != current_user.id and current_user.role not in ['admin', 'professeur']:
        return jsonify({'success': False, 'message': 'Non autorisé'}), 403
    
    # Supprimer d'abord les participants
    ProjectParticipant.query.filter_by(project_id=project.id).delete()
    
    # Puis supprimer le projet
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'success': True})

@project_bp.route('/add_participant/<int:project_id>', methods=['GET', 'POST'])
@login_required
def add_participant(project_id):
    """Ajoute un participant à un projet"""
    project = Project.query.get_or_404(project_id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if project.owner_id != current_user.id and current_user.role not in ['admin', 'professeur']:
        flash('Vous n\'êtes pas autorisé à modifier ce projet.', 'danger')
        return redirect(url_for('project.index'))
    
    lang = session.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        
        if user_id and user_id.isdigit():
            user_id = int(user_id)
            
            # Vérifier que l'utilisateur n'est pas déjà participant
            existing = ProjectParticipant.query.filter_by(
                project_id=project.id,
                user_id=user_id
            ).first()
            
            if existing:
                flash('Cet utilisateur est déjà participant au projet.', 'warning')
            else:
                participant = ProjectParticipant(
                    project_id=project.id,
                    user_id=user_id,
                    role='member'
                )
                db.session.add(participant)
                db.session.commit()
                flash('Participant ajouté avec succès.', 'success')
        
        return redirect(url_for('project.edit_project', project_id=project.id))
    
    # Récupérer tous les utilisateurs qui ne sont pas déjà participants
    current_participants = [p.user_id for p in project.participants]
    available_users = User.query.filter(User.id.notin_(current_participants)).all()
    
    return render_template('add_participant.html', project=project, 
                          available_users=available_users, labels=labels)

@project_bp.route('/remove_participant/<int:project_id>/<int:user_id>', methods=['POST'])
@login_required
def remove_participant(project_id, user_id):
    """Supprime un participant d'un projet"""
    project = Project.query.get_or_404(project_id)
    
    # Vérifier que l'utilisateur est le propriétaire ou un administrateur
    if project.owner_id != current_user.id and current_user.role not in ['admin', 'professeur']:
        return jsonify({'success': False, 'message': 'Non autorisé'}), 403
    
    # Vérifier que l'utilisateur n'est pas le propriétaire
    if int(user_id) == project.owner_id:
        return jsonify({'success': False, 'message': 'Impossible de supprimer le propriétaire du projet'}), 400
    
    # Supprimer le participant
    participant = ProjectParticipant.query.filter_by(
        project_id=project.id,
        user_id=user_id
    ).first()
    
    if participant:
        db.session.delete(participant)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Participant non trouvé'}), 404
