from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db, csrf
from app.models import WelcomeMessage, User
from datetime import datetime

welcome_bp = Blueprint('welcome', __name__, url_prefix='/welcome')

@welcome_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_welcome():
    # Vérifier si l'utilisateur est un administrateur ou un professeur
    if current_user.role not in ['admin', 'professeur']:
        flash("Vous n'avez pas les droits pour accéder à cette page.", "error")
        return redirect(url_for('dashboard.home'))
    
    # Récupérer le message de bienvenue actuel ou en créer un nouveau s'il n'existe pas
    welcome_message = WelcomeMessage.query.order_by(WelcomeMessage.id.desc()).first()
    if not welcome_message:
        welcome_message = WelcomeMessage(
            content="Bienvenue sur votre espace élève Pyteur!",
            created_by_id=current_user.id
        )
        db.session.add(welcome_message)
        db.session.commit()
    
    # Traiter le formulaire si c'est une requête POST
    if request.method == 'POST':
        content = request.form.get('content')
        
        # Créer un nouveau message de bienvenue
        new_message = WelcomeMessage(
            content=content,
            created_by_id=current_user.id
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        flash("Le message de bienvenue a été mis à jour avec succès.", "success")
        return redirect(url_for('welcome.edit_welcome'))
    
    # Récupérer l'historique des messages de bienvenue
    message_history = WelcomeMessage.query.order_by(WelcomeMessage.created_at.desc()).all()
    
    return render_template('edit_welcome.html', 
                           welcome_message=welcome_message,
                           message_history=message_history)

@welcome_bp.route('/get_latest')
def get_latest():
    # Récupérer le dernier message de bienvenue
    welcome_message = WelcomeMessage.query.order_by(WelcomeMessage.id.desc()).first()
    
    if not welcome_message:
        # Créer un message par défaut si aucun n'existe
        welcome_message = WelcomeMessage(
            content="Bienvenue sur votre espace élève Pyteur!",
            created_by_id=None
        )
        db.session.add(welcome_message)
        db.session.commit()
    
    return {
        'content': welcome_message.content,
        'updated_at': welcome_message.updated_at.strftime('%d/%m/%Y %H:%M'),
        'created_by': welcome_message.created_by.prenom + ' ' + welcome_message.created_by.nom if welcome_message.created_by else 'Système'
    }
