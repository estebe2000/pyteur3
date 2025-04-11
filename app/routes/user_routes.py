from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, csrf
from app.models import User, Group, SchoolClass
import os
import csv
import datetime
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login')
        password = request.form.get('password')
        
        user = User.query.filter_by(login=login_input).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'eleve':
                return redirect(url_for('eleve.dashboard'))
            else:
                return redirect(url_for('dashboard.home'))
        
        flash('Login ou mot de passe incorrect.')
    return render_template('login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@user_bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    eleves = User.query.filter_by(role='eleve').order_by(User.nom).all()
    profs = User.query.filter_by(role='professeur').order_by(User.nom).all()
    admins = User.query.filter_by(role='admin').order_by(User.nom).all()
    return render_template('users.html', eleves=eleves, profs=profs, admins=admins)

@user_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
        
    if request.method == 'POST':
        import secrets
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
        return redirect(url_for('user.users'))
    
    return render_template('add_user.html')

@user_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
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
                user.date_naissance = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                user.date_naissance = None
        else:
            user.date_naissance = None

        password = request.form.get('password')
        if password:
            user.password = generate_password_hash(password)

        user.besoins_particuliers = request.form.get('besoins_particuliers')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        
        db.session.commit()
        flash("Utilisateur mis à jour avec succès")
        return redirect(url_for('user.users'))
        
    return render_template('edit_user.html', user=user)

@user_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required 
def delete_user(id):
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé avec succès")
    return redirect(url_for('user.users'))

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    import json

    config_path = os.path.join(os.path.dirname(__file__), '..', 'drive_config.json')
    config_path = os.path.abspath(config_path)

    # Charger la config existante
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config_data = json.load(f)
            except json.JSONDecodeError:
                config_data = {}
    else:
        config_data = {}

    if request.method == 'POST':
        current_user.nom = request.form.get('nom')
        current_user.prenom = request.form.get('prenom')
        current_user.login = request.form.get('login')
        current_user.email = request.form.get('email')

        date_str = request.form.get('date_naissance')
        if date_str:
            try:
                current_user.date_naissance = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                current_user.date_naissance = None
        else:
            current_user.date_naissance = None

        current_user.besoins_particuliers = request.form.get('besoins_particuliers')
        password = request.form.get('password')
        if password:
            current_user.password = generate_password_hash(password)
        db.session.commit()

        # Mettre à jour l'URL du drive si fournie
        drive_url = request.form.get('drive_url')
        if drive_url:
            config_data['drive_url'] = drive_url
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        flash('Profil mis à jour avec succès.')

    # Passer l'URL du drive au template
    drive_url = config_data.get('drive_url', 'https://nuage.apps.education.fr/')
    return render_template('settings.html', user=current_user, drive_url=drive_url)

@user_bp.route('/users/import', methods=['GET', 'POST'])
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

        base = os.path.basename(filename)
        parts = base.split('.')
        classe_nom = parts[0]
        groupe_nom = parts[1] if len(parts) > 1 else 'default'

        school_class = SchoolClass.query.filter_by(nom=classe_nom).first()
        if not school_class:
            school_class = SchoolClass(nom=classe_nom, niveau='Inconnu')
            db.session.add(school_class)
            db.session.commit()

        group = Group.query.filter_by(nom=groupe_nom, class_id=school_class.id).first()
        if not group:
            group = Group(nom=groupe_nom, class_id=school_class.id)
            db.session.add(group)
            db.session.commit()

        with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            headers = next(reader, None)
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
        return redirect(url_for('user.users'))

    return render_template('import_users.html')

@user_bp.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in ['fr', 'en']:
        session['lang'] = lang_code
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('dashboard.home'))
