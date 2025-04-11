from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, Response
from flask_login import login_required, current_user
from app import db, csrf
from app.models import Document, ExerciseAssignment, User, Group, SchoolClass
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import json

exercise_bp = Blueprint('exercise', __name__)

@exercise_bp.route('/exercises')
@login_required
def exercises():
    personal_exercises = Document.query.filter_by(user_id=current_user.id, type='exercise')

    filters = [ExerciseAssignment.user_id == current_user.id]

    if current_user.group_id is not None:
        filters.append(ExerciseAssignment.group_id == current_user.group_id)

    if current_user.group and current_user.group.school_class:
        filters.append(ExerciseAssignment.class_id == current_user.group.school_class.id)

    assigned_exercises = Document.query.join(ExerciseAssignment).filter(
        Document.type == 'exercise',
        or_(*filters)
    )

    exercises = personal_exercises.union(assigned_exercises).all()

    return render_template('exercises.html', exercises=exercises)

@exercise_bp.route('/upload_exercise', methods=['POST'])
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
        return redirect(url_for('eleve.dashboard'))
    
    flash('Type de fichier non autorisé (py, sql, js, ml, xcas uniquement)')
    return redirect(url_for('eleve.dashboard'))

@exercise_bp.route('/assign_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def assign_exercise(exercise_id):
    if current_user.role != 'admin':
        return "Accès non autorisé", 403

    from app.models import User, Group, SchoolClass, ExerciseAssignment, Document

    exercise = Document.query.get_or_404(exercise_id)

    if request.method == 'POST':
        ExerciseAssignment.query.filter_by(exercise_id=exercise_id).delete()

        user_ids = request.form.getlist('users')
        for uid in user_ids:
            assign = ExerciseAssignment(exercise_id=exercise_id, user_id=int(uid))
            db.session.add(assign)

        group_ids = request.form.getlist('groups')
        for gid in group_ids:
            assign = ExerciseAssignment(exercise_id=exercise_id, group_id=int(gid))
            db.session.add(assign)

        class_ids = request.form.getlist('classes')
        for cid in class_ids:
            assign = ExerciseAssignment(exercise_id=exercise_id, class_id=int(cid))
            db.session.add(assign)

        db.session.commit()
        flash("Affectations mises à jour")
        return redirect(url_for('exercise.exercises'))

    users = User.query.filter_by(role='eleve').all()
    groups = Group.query.all()
    classes = SchoolClass.query.all()

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

@csrf.exempt
@exercise_bp.route('/delete_exercise/<int:ex_id>', methods=['POST'])
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

@exercise_bp.route('/createur_exercice', methods=['GET', 'POST'])
@login_required
def createur_exercice():
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

@exercise_bp.route('/generateur_exercice')
@login_required
def generateur_exercice():
    from app.ia_providers import provider_manager
    ia_name = provider_manager.active_provider_name or "Aucun fournisseur"
    model_name = provider_manager.active_provider.model if provider_manager.active_provider else "Aucun modèle"
    return render_template('generateur_exercice.html', ia_name=ia_name, model_name=model_name)

@exercise_bp.route('/exercices_flash')
@login_required
def exercices_flash():
    from app.ia_providers import provider_manager
    ia_name = provider_manager.active_provider_name or "Aucun fournisseur"
    model_name = provider_manager.active_provider.model if provider_manager.active_provider else "Aucun modèle"
    return render_template('exercices_flash.html', ia_name=ia_name, model_name=model_name)

@exercise_bp.route('/api/generateur_data', methods=['GET'])
@login_required
def api_generateur_data():
    try:
        with open('app/static/data/data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@csrf.exempt
@exercise_bp.route('/api/generer_exercice', methods=['POST'])
@login_required
def api_generer_exercice():
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

        from app.prompts_generateur import prompt_generation_exercice
        prompt = prompt_generation_exercice(niveau, theme, difficulte, description, debutant=debutant)

        from app.ia_client import generate_text
        reponse = generate_text(prompt)

        return jsonify({'prompt': prompt, 'response': reponse})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@csrf.exempt
@exercise_bp.route('/api/evaluer_code', methods=['POST'])
@login_required
def api_evaluer_code():
    try:
        data = request.get_json(force=True)
        code = data.get('code')
        enonce = data.get('enonce')

        if not code or not enonce:
            return {'error': 'Paramètres manquants'}, 400

        from app.prompts_generateur import prompt_evaluation_code
        prompt = prompt_evaluation_code(code, enonce)

        from app.ia_client import generate_text
        reponse = generate_text(prompt)

        return {'prompt': prompt, 'response': reponse}
    except Exception as e:
        return {'error': str(e)}, 500

@csrf.exempt
@exercise_bp.route('/api/upload_notebook', methods=['POST'])
@login_required
def api_upload_notebook():
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
