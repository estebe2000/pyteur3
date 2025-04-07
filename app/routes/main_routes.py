from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Document, SchoolClass, Group

main_bp = Blueprint('main', __name__)

@main_bp.route('/qcm')
@login_required
def qcm():
    return render_template('qcm.html')

@main_bp.route('/statistiques')
@login_required
def statistiques():
    return render_template('statistiques.html')

@main_bp.route('/messagerie')
@login_required
def messagerie():
    return render_template('messagerie.html')

@main_bp.route('/todo')
@login_required
def todo():
    return render_template('todo.html')

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
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        
        flash('Email ou mot de passe incorrect.')
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/documents')
@login_required
def documents():
    docs = Document.query.filter_by(type='document').all()
    return render_template('documents.html', documents=docs)

@main_bp.route('/exercises')
@login_required
def exercises():
    exercises = Document.query.filter_by(user_id=current_user.id, type='exercise').all()
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
    users_list = User.query.order_by(User.nom).all()
    return render_template('users.html', users=users_list)

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
        user.date_naissance = request.form.get('date_naissance')
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
        from mistral_client import generate_text
        ai_response = generate_text(user_message)
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
