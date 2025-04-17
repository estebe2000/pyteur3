from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app, send_file, flash
from flask_login import current_user
import os
import json
import uuid
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models import db, User, Document, SchoolClass, ExerciseAssignment, Rubrique
from app.ia_client import generate_text
from app.prompts_generateur import prompt_generation_exercice, HTML_FORMATTING_INSTRUCTIONS
import tempfile

exercise_bp = Blueprint('exercise', __name__)

# Répertoire pour les fichiers temporaires
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'pyteur_temp')
os.makedirs(TEMP_DIR, exist_ok=True)

def generate_exercise(niveau, theme, difficulte, description, debutant):
    """
    Génère un exercice en utilisant l'IA.
    
    Args:
        niveau (str): Niveau scolaire (ex: "Terminale")
        theme (str): Thème de l'exercice
        difficulte (int): Niveau de difficulté (1-5)
        description (str): Description de l'exercice
        debutant (bool): Si l'exercice est pour un débutant
        
    Returns:
        tuple: (prompt, response) Le prompt utilisé et la réponse de l'IA
    """
    prompt = prompt_generation_exercice(niveau, theme, difficulte, description, debutant)
    response = generate_text(prompt, max_tokens=1024, temperature=0.7)
    return prompt, response

@exercise_bp.route('/api/generateur_data')
def generateur_data():
    try:
        with open(os.path.join(current_app.root_path, 'static', 'data', 'data.json'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@exercise_bp.route('/api/generer_exercice', methods=['POST'])
def generer_exercice():
    try:
        # Récupérer les données JSON
        data = request.json
        current_app.logger.info(f"Données reçues: {data}")
        
        if not data:
            current_app.logger.error("Données JSON manquantes")
            return jsonify({"error": "Données JSON manquantes"}), 400
            
        niveau = data.get('niveau')
        theme = data.get('theme')
        difficulte = data.get('difficulte')
        description = data.get('description')
        debutant = data.get('debutant', False)
        
        current_app.logger.info(f"Paramètres: niveau={niveau}, theme={theme}, difficulte={difficulte}, description={description}, debutant={debutant}")
        
        # Vérifier que tous les paramètres requis sont présents
        if not niveau or not theme or not difficulte or not description:
            missing = []
            if not niveau: missing.append("niveau")
            if not theme: missing.append("theme")
            if not difficulte: missing.append("difficulte")
            if not description: missing.append("description")
            current_app.logger.error(f"Paramètres manquants: {', '.join(missing)}")
            return jsonify({"error": f"Paramètres manquants: {', '.join(missing)}"}), 400
        
        # Convertir difficulte en entier si c'est une chaîne
        if isinstance(difficulte, str) and difficulte.isdigit():
            difficulte = int(difficulte)
        
        current_app.logger.info(f"Difficulté après conversion: {difficulte} (type: {type(difficulte)})")
        
        # Générer l'exercice
        prompt = prompt_generation_exercice(niveau, theme, difficulte, description, debutant)
        current_app.logger.info("Prompt généré avec succès")
        
        # Utiliser un texte par défaut si l'IA n'est pas disponible
        try:
            current_app.logger.info("Appel à generate_text...")
            response = generate_text(prompt, max_tokens=1024, temperature=0.7)
            current_app.logger.info(f"Réponse de l'IA reçue: {response[:100]}...")
            
            if response.startswith("Erreur"):
                current_app.logger.error(f"Erreur IA: {response}")
                response = f"L'IA n'est pas disponible actuellement. Voici l'énoncé de l'exercice:\n\n# Exercice sur {theme}\n\nNiveau: {niveau}, Difficulté: {difficulte}/5\n\n{description}\n\n```python\n# Votre code ici\n```"
        except Exception as e:
            current_app.logger.exception("Erreur lors de la génération du texte")
            response = f"L'IA n'est pas disponible actuellement. Voici l'énoncé de l'exercice:\n\n# Exercice sur {theme}\n\nNiveau: {niveau}, Difficulté: {difficulte}/5\n\n{description}\n\n```python\n# Votre code ici\n```"

        current_app.logger.info("Envoi de la réponse au client")
        return jsonify({"prompt": prompt, "response": response})
    except (json.JSONDecodeError, OSError) as e:
        current_app.logger.exception("Erreur lors du traitement de la requête")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.exception("Erreur inattendue lors de la génération de l'exercice")
        return jsonify({"error": str(e)}), 500

@exercise_bp.route('/api/upload_notebook', methods=['POST'])
def upload_notebook():
    try:
        notebook_data = request.json
        
        # Créer le répertoire s'il n'existe pas
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'temp')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Enregistrer le notebook dans le répertoire static
        with open(os.path.join(upload_dir, '1_programme_nsi_terminal.ipynb'), 'w', encoding='utf-8') as f:
            json.dump(notebook_data, f, ensure_ascii=False, indent=2)
        
        # Stocker également dans le répertoire temporaire
        notebook_id = str(uuid.uuid4())
        notebook_path = os.path.join(TEMP_DIR, f"{notebook_id}.ipynb")
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({"success": True, "id": notebook_id})
    except Exception as e:
        return jsonify({"error": str(e)})

@exercise_bp.route('/api/evaluer_code', methods=['POST'])
def evaluer_code():
    try:
        data = request.json
        code = data.get('code', '')
        enonce = data.get('enonce', '')
        
        current_app.logger.info(f"Évaluation de code reçue. Longueur du code: {len(code)} caractères")
        
        if not code or not enonce:
            current_app.logger.error("Code ou énoncé manquant")
            return jsonify({"error": "Code ou énoncé manquant"}), 400
        
        # Générer le prompt d'évaluation
        from app.prompts_generateur import prompt_evaluation_code
        prompt = prompt_evaluation_code(code, enonce)
        current_app.logger.info("Prompt d'évaluation généré")
        
        # Utiliser l'IA pour évaluer le code
        try:
            current_app.logger.info("Appel à generate_text pour l'évaluation...")
            response = generate_text(prompt, max_tokens=1024, temperature=0.7)
            current_app.logger.info(f"Réponse d'évaluation reçue: {response[:100]}...")
            
            if response.startswith("Erreur"):
                current_app.logger.error(f"Erreur IA: {response}")
                response = "<h1>Évaluation du code</h1><p>L'IA n'est pas disponible actuellement pour évaluer votre code.</p>"
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'évaluation du code: {str(e)}")
            response = f"<h1>Évaluation du code</h1><p>Erreur lors de l'évaluation: {str(e)}</p>"
        
        current_app.logger.info("Envoi de la réponse d'évaluation au client")
        return jsonify({"response": response, "prompt": prompt})
    except Exception as e:
        current_app.logger.error(f"Erreur dans evaluer_code: {str(e)}")
        return jsonify({"error": str(e)}), 500

@exercise_bp.route('/exercises')
def exercises():
    """Page des exercices"""
    # Vérifier si la requête vient d'un iframe
    is_iframe = request.args.get('iframe', 'false') == 'true'
    
    # Récupérer les labels pour le titre
    from app.lang.lang_fr import LABELS as labels_fr
    from app.lang.lang_en import LABELS as labels_en
    lang = request.cookies.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    # Vérifier si l'utilisateur est un professeur ou un administrateur
    is_teacher = current_user.role in ['admin', 'professeur']
    
    # Exercices personnels (créés par l'utilisateur)
    personal_exercises = Document.query.filter_by(user_id=current_user.id, type='exercise').all()
    
    # Exercices partagés (affectés à l'utilisateur)
    filters = [ExerciseAssignment.user_id == current_user.id]
    
    if current_user.group_id is not None:
        filters.append(ExerciseAssignment.group_id == current_user.group_id)
    
    if current_user.group and current_user.group.school_class:
        filters.append(ExerciseAssignment.class_id == current_user.group.school_class.id)
    
    from sqlalchemy import or_
    assigned_exercises = Document.query.join(ExerciseAssignment).filter(
        Document.type == 'exercise',
        or_(*filters)
    ).all()
    
    # Récupérer toutes les rubriques
    rubriques = Rubrique.query.all()
    
    # Organiser les exercices par rubrique
    exercises_by_rubrique = {}
    
    # Initialiser avec "Non classé" pour les exercices sans rubrique
    exercises_by_rubrique['non_classe'] = {
        'nom': 'Non classé',
        'description': 'Exercices sans rubrique',
        'exercises': []
    }
    
    # Initialiser avec toutes les rubriques existantes
    for rubrique in rubriques:
        exercises_by_rubrique[rubrique.id] = {
            'nom': rubrique.nom,
            'description': rubrique.description,
            'exercises': []
        }
    
    # Organiser les exercices partagés par rubrique
    for ex in assigned_exercises:
        # Trouver l'affectation pour cet exercice
        assignment = ExerciseAssignment.query.filter_by(exercise_id=ex.id).first()
        
        if assignment and assignment.rubrique_id and assignment.rubrique_id in exercises_by_rubrique:
            exercises_by_rubrique[assignment.rubrique_id]['exercises'].append(ex)
        else:
            exercises_by_rubrique['non_classe']['exercises'].append(ex)
    
    return render_template('exercises.html', 
                          personal_exercises=personal_exercises,
                          exercises_by_rubrique=exercises_by_rubrique,
                          is_teacher=is_teacher,
                          labels=labels)

@exercise_bp.route('/createur_exercice', methods=['GET', 'POST'])
def createur_exercice():
    """Page du créateur d'exercices"""
    if request.method == 'POST':
        try:
            # Récupérer les données JSON du formulaire
            json_data = request.form.get('json_data')
            if json_data:
                # Enregistrer les données dans le fichier data.json
                with open(os.path.join(current_app.root_path, 'static', 'data', 'data.json'), 'w', encoding='utf-8') as f:
                    f.write(json_data)
                flash('Données enregistrées avec succès', 'success')
            else:
                flash('Aucune donnée à enregistrer', 'error')
            return redirect(url_for('exercise.createur_exercice'))
        except Exception as e:
            current_app.logger.error(f"Erreur lors de l'enregistrement des données: {str(e)}")
            flash(f'Erreur lors de l\'enregistrement des données: {str(e)}', 'error')
            return redirect(url_for('exercise.createur_exercice'))
    else:
        try:
            with open(os.path.join(current_app.root_path, 'static', 'data', 'data.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
            return render_template('createur_exercice.html', data_json=json.dumps(data))
        except Exception as e:
            current_app.logger.error(f"Erreur lors du chargement des données: {str(e)}")
            return render_template('createur_exercice.html', data_json=json.dumps({}))

@exercise_bp.route('/generateur_exercice')
def generateur_exercice():
    """Page du générateur d'exercices"""
    # Récupérer les informations sur l'IA et le modèle
    ia_name = current_app.config.get('IA_NAME', 'IA locale')
    model_name = current_app.config.get('MODEL_NAME', 'Modèle par défaut')
    
    # Récupérer les labels pour les traductions
    from app.lang.lang_fr import LABELS as labels_fr
    
    return render_template('generateur_exercice.html', 
                          ia_name=ia_name, 
                          model_name=model_name,
                          labels=labels_fr)

@exercise_bp.route('/exercices_flash')
def exercices_flash():
    """Page des exercices flash"""
    # Récupérer les informations sur l'IA et le modèle
    ia_name = current_app.config.get('IA_NAME', 'IA locale')
    model_name = current_app.config.get('MODEL_NAME', 'Modèle par défaut')
    
    # Récupérer les labels pour les traductions
    from app.lang.lang_fr import LABELS as labels_fr
    
    return render_template('exercices_flash.html', 
                          ia_name=ia_name, 
                          model_name=model_name,
                          labels=labels_fr)

@exercise_bp.route('/upload_exercise', methods=['POST'])
def upload_exercise():
    """Télécharger un exercice"""
    try:
        if 'file' in request.files:
            # Téléchargement de fichier
            file = request.files['file']
            if file.filename == '':
                flash('Aucun fichier sélectionné', 'error')
                return redirect(url_for('exercise.exercises'))
            
            # Sécuriser le nom du fichier
            filename = secure_filename(file.filename)

            # Vérifier le type de fichier
            if not filename.endswith(('.py', '.ipynb')):
                flash('Type de fichier non autorisé. Seuls les fichiers .py et .ipynb sont autorisés.', 'error')
                return redirect(url_for('exercise.exercises'))
            
            # Créer une structure de répertoires organisée
            # Format: uploads/exercises/[année]/[utilisateur_id]/
            current_year = datetime.now().strftime('%Y')
            user_folder = str(current_user.id)
            
            # Chemin relatif pour la base de données (utiliser des slashes pour les URLs)
            relative_path = f"exercises/{current_year}/{user_folder}"
            
            # Chemin complet pour le stockage
            upload_folder = os.path.join('app', 'static', 'uploads', relative_path.replace('/', os.sep))
            
            # Créer les répertoires s'ils n'existent pas
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder, exist_ok=True)
            
            # Générer un nom de fichier unique avec timestamp pour éviter les collisions
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Chemin complet du fichier
            file_path = os.path.join(upload_folder, unique_filename)
            
            # Chemin relatif pour la base de données (ce qui sera stocké)
            db_filename = f"{relative_path}/{unique_filename}"
            
            # Enregistrer le fichier
            file.save(file_path)
            
            # Récupérer les tags
            tags = request.form.get('tags', '')
            
            # Créer un document dans la base de données
            document = Document(
                filename=db_filename,
                original_filename=filename,
                type='exercise',
                tags=tags,
                user_id=current_user.id
            )
            db.session.add(document)
            db.session.commit()
            
            flash('Exercice téléchargé avec succès', 'success')
        elif 'code' in request.form or 'code_textarea' in request.form:
            # Ajout de code depuis l'éditeur
            code = request.form.get('code') or request.form.get('code_textarea')
            if not code:
                flash('Aucun code fourni', 'error')
                return redirect(url_for('exercise.exercises'))
            
            # Créer une structure de répertoires organisée
            # Format: uploads/exercises/[année]/[utilisateur_id]/
            current_year = datetime.now().strftime('%Y')
            user_folder = str(current_user.id)
            
            # Chemin relatif pour la base de données (utiliser des slashes pour les URLs)
            relative_path = f"exercises/{current_year}/{user_folder}"
            
            # Chemin complet pour le stockage
            upload_folder = os.path.join('app', 'static', 'uploads', relative_path.replace('/', os.sep))
            
            # Créer les répertoires s'ils n'existent pas
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder, exist_ok=True)
            
            # Générer un nom de fichier unique avec timestamp pour éviter les collisions
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}.py"
            
            # Chemin complet du fichier
            file_path = os.path.join(upload_folder, unique_filename)
            
            # Chemin relatif pour la base de données (ce qui sera stocké)
            db_filename = f"{relative_path}/{unique_filename}"
            
            # Enregistrer le fichier
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Récupérer les tags
            tags = request.form.get('tags', '')
            
            # Créer un document dans la base de données
            document = Document(
                filename=db_filename,
                original_filename=unique_filename,
                type='exercise',
                tags=tags,
                user_id=current_user.id
            )
            db.session.add(document)
            db.session.commit()
            
            flash('Exercice ajouté avec succès', 'success')
        else:
            flash('Aucun fichier ou code fourni', 'error')
        
        return redirect(url_for('exercise.exercises'))
    except Exception as e:
        flash(f'Erreur lors du téléchargement de l\'exercice: {str(e)}', 'error')
        return redirect(url_for('exercise.exercises'))

@exercise_bp.route('/assign_exercise/<int:exercise_id>', methods=['GET', 'POST'])
def assign_exercise(exercise_id):
    """Affecter un exercice à des élèves"""
    exercise = Document.query.get_or_404(exercise_id)
    
    if request.method == 'POST':
        try:
            # Supprimer les affectations existantes
            ExerciseAssignment.query.filter_by(exercise_id=exercise_id).delete()
            
            # Récupérer les utilisateurs, groupes et classes sélectionnés
            user_ids = request.form.getlist('users')
            group_ids = request.form.getlist('groups')
            class_ids = request.form.getlist('classes')
            rubrique_id = request.form.get('rubrique_id')
            
            # Récupérer les informations de notification
            notification_message = request.form.get('notification_message', '').strip()
            send_notification = 'send_notification' in request.form
            
            # Convertir en entier si une rubrique est sélectionnée
            if rubrique_id and rubrique_id != '':
                rubrique_id = int(rubrique_id)
            else:
                rubrique_id = None
            
            # Créer les nouvelles affectations pour les utilisateurs
            for user_id in user_ids:
                assignment = ExerciseAssignment(
                    exercise_id=exercise_id,
                    user_id=int(user_id),
                    rubrique_id=rubrique_id
                )
                db.session.add(assignment)
            
            # Créer les nouvelles affectations pour les groupes
            for group_id in group_ids:
                assignment = ExerciseAssignment(
                    exercise_id=exercise_id,
                    group_id=int(group_id),
                    rubrique_id=rubrique_id
                )
                db.session.add(assignment)
            
            # Créer les nouvelles affectations pour les classes
            for class_id in class_ids:
                assignment = ExerciseAssignment(
                    exercise_id=exercise_id,
                    class_id=int(class_id),
                    rubrique_id=rubrique_id
                )
                db.session.add(assignment)
            
            db.session.commit()
            
            # Envoyer une notification si demandé
            if send_notification and (user_ids or group_ids or class_ids):
                # Importer les modèles de messagerie
                from app.models import Message, MessageRecipient
                
                # Créer un message par défaut si aucun message n'est fourni
                if not notification_message:
                    rubrique_info = ""
                    if rubrique_id:
                        rubrique = Rubrique.query.get(rubrique_id)
                        if rubrique:
                            rubrique_info = f" dans la rubrique '{rubrique.nom}'"
                    
                    notification_message = f"Un nouvel exercice '{exercise.original_filename}' vous a été affecté{rubrique_info}."
                
                # Créer le message
                message = Message(sender_id=current_user.id, content=notification_message)
                db.session.add(message)
                db.session.flush()  # Pour obtenir l'ID du message
                
                # Créer les destinataires
                recipients = []
                
                # Ajouter les utilisateurs comme destinataires
                for user_id in user_ids:
                    recipients.append(MessageRecipient(
                        message_id=message.id,
                        recipient_user_id=int(user_id)
                    ))
                
                # Ajouter les groupes comme destinataires
                for group_id in group_ids:
                    recipients.append(MessageRecipient(
                        message_id=message.id,
                        recipient_group_id=int(group_id)
                    ))
                
                # Ajouter les classes comme destinataires (via leurs groupes)
                for class_id in class_ids:
                    school_class = SchoolClass.query.get(class_id)
                    if school_class:
                        groups = school_class.groups
                        for group in groups:
                            recipients.append(MessageRecipient(
                                message_id=message.id,
                                recipient_group_id=group.id
                            ))
                
                # Enregistrer les destinataires
                if recipients:
                    db.session.add_all(recipients)
                    db.session.commit()
                    flash('Affectations enregistrées et notifications envoyées avec succès', 'success')
                else:
                    flash('Affectations enregistrées avec succès, mais aucune notification n\'a été envoyée (aucun destinataire valide)', 'warning')
            else:
                flash('Affectations enregistrées avec succès', 'success')
            
            return redirect(url_for('exercise.exercises'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de l'affectation de l'exercice: {str(e)}")
            flash(f'Erreur lors de l\'affectation de l\'exercice: {str(e)}', 'error')
            return redirect(url_for('exercise.exercises'))
    
    # Récupérer les utilisateurs, groupes et classes
    users = User.query.filter_by(role='eleve').all()
    classes = SchoolClass.query.all()
    groups = []  # À remplacer par la récupération des groupes si vous avez une table correspondante
    rubriques = Rubrique.query.all()
    
    # Récupérer les affectations existantes
    assignments = ExerciseAssignment.query.filter_by(exercise_id=exercise_id).all()
    assigned_users = [a.user_id for a in assignments if a.user_id is not None]
    assigned_groups = [a.group_id for a in assignments if a.group_id is not None]
    assigned_classes = [a.class_id for a in assignments if a.class_id is not None]
    
    # Récupérer la rubrique si elle existe
    current_rubrique_id = None
    if assignments and assignments[0].rubrique_id:
        current_rubrique_id = assignments[0].rubrique_id
    
    return render_template('assign_exercise.html', 
                          exercise=exercise, 
                          users=users,
                          groups=groups,
                          classes=classes,
                          rubriques=rubriques,
                          assigned_users=assigned_users,
                          assigned_groups=assigned_groups,
                          assigned_classes=assigned_classes,
                          current_rubrique_id=current_rubrique_id)

@exercise_bp.route('/api/store_temp_script', methods=['POST'])
def store_temp_script():
    """Stocke temporairement un script Python dans un fichier et renvoie un ID unique"""
    try:
        data = request.json
        script_content = data.get('script', '')
        
        # Générer un ID unique
        script_id = str(uuid.uuid4())
        
        # Créer le fichier temporaire
        script_path = os.path.join(TEMP_DIR, f"{script_id}.py")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Nettoyer les anciens fichiers (plus de 1 heure)
        current_time = time.time()
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
                try:
                    os.remove(file_path)
                except:
                    pass
        
        return jsonify({"id": script_id})
    except Exception as e:
        return jsonify({"error": str(e)})

@exercise_bp.route('/api/get_temp_script/<script_id>')
def get_temp_script(script_id):
    """Récupère un script Python temporaire par son ID"""
    try:
        script_path = os.path.join(TEMP_DIR, f"{script_id}.py")
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "# Script non trouvé ou expiré"
    except Exception as e:
        return f"# Erreur: {str(e)}"

@exercise_bp.route('/api/get_temp_notebook/<notebook_id>')
def get_temp_notebook(notebook_id):
    """Récupère un notebook Jupyter temporaire par son ID"""
    try:
        notebook_path = os.path.join(TEMP_DIR, f"{notebook_id}.ipynb")
        if os.path.exists(notebook_path):
            with open(notebook_path, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        else:
            return jsonify({"error": "Notebook non trouvé ou expiré"})
    except Exception as e:
        return jsonify({"error": str(e)})

@exercise_bp.route('/prompt_editor')
def prompt_editor():
    """Page de l'éditeur de prompts"""
    # Récupérer les informations sur l'IA et le modèle
    ia_name = current_app.config.get('IA_NAME', 'IA locale')
    model_name = current_app.config.get('MODEL_NAME', 'Modèle par défaut')
    
    # Récupérer les labels pour les traductions
    from app.lang.lang_fr import LABELS as labels_fr
    from app.lang.lang_en import LABELS as labels_en
    lang = request.cookies.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    # Récupérer les prompts personnalisés s'ils existent
    try:
        with open(os.path.join(current_app.root_path, 'prompts_config.json'), 'r', encoding='utf-8') as f:
            prompts_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        prompts_config = {
            "generation": None,
            "evaluation": None,
            "html_formatting": None
        }
    
    # Récupérer les prompts par défaut depuis le module prompts_generateur
    from app.prompts_generateur import prompt_generation_exercice, prompt_evaluation_code, HTML_FORMATTING_INSTRUCTIONS
    
    # Utiliser les prompts personnalisés s'ils existent, sinon utiliser les prompts par défaut
    generation_prompt = prompts_config.get('generation') or prompt_generation_exercice("Niveau", "Theme", 3, "Description", False)
    evaluation_prompt = prompts_config.get('evaluation') or prompt_evaluation_code("code", "enonce")
    html_formatting = prompts_config.get('html_formatting') or HTML_FORMATTING_INSTRUCTIONS
    
    # Extraire le corps des fonctions pour obtenir uniquement le texte du prompt
    import inspect
    
    # Pour le prompt de génération, on extrait le corps de la fonction
    generation_prompt_default = inspect.getsource(prompt_generation_exercice)
    generation_prompt_default = generation_prompt_default.split('return f"""')[1].split('"""')[0]
    
    # Pour le prompt d'évaluation, on extrait le corps de la fonction
    evaluation_prompt_default = inspect.getsource(prompt_evaluation_code)
    evaluation_prompt_default = evaluation_prompt_default.split('return f"""')[1].split('"""')[0]
    
    return render_template('prompt_editor.html',
                          ia_name=ia_name,
                          model_name=model_name,
                          labels=labels,
                          generation_prompt=generation_prompt,
                          evaluation_prompt=evaluation_prompt,
                          default_generation_prompt=generation_prompt_default,
                          default_evaluation_prompt=evaluation_prompt_default,
                          default_html_formatting=HTML_FORMATTING_INSTRUCTIONS)

@exercise_bp.route('/api/save_prompt', methods=['POST'])
def save_prompt():
    """Sauvegarde un prompt personnalisé"""
    try:
        data = request.json
        prompt_type = data.get('type')
        content = data.get('content')
        
        if not prompt_type or not content:
            return jsonify({"success": False, "error": "Type de prompt ou contenu manquant"}), 400
        
        # Vérifier que le type de prompt est valide
        if prompt_type not in ['generation', 'evaluation', 'html_formatting']:
            return jsonify({"success": False, "error": "Type de prompt invalide"}), 400
        
        # Charger la configuration actuelle
        try:
            with open(os.path.join(current_app.root_path, 'prompts_config.json'), 'r', encoding='utf-8') as f:
                prompts_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            prompts_config = {
                "generation": None,
                "evaluation": None,
                "html_formatting": None
            }
        
        # Mettre à jour le prompt
        prompts_config[prompt_type] = content
        
        # Sauvegarder la configuration
        with open(os.path.join(current_app.root_path, 'prompts_config.json'), 'w', encoding='utf-8') as f:
            json.dump(prompts_config, f, ensure_ascii=False, indent=4)
        
        return jsonify({"success": True})
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la sauvegarde du prompt: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@exercise_bp.route('/api/test_prompt', methods=['POST'])
def test_prompt():
    """Teste un prompt personnalisé"""
    try:
        data = request.json
        prompt_type = data.get('type')
        prompt_content = data.get('prompt')
        params = data.get('params', {})
        
        if not prompt_type or not prompt_content:
            return jsonify({"success": False, "error": "Type de prompt ou contenu manquant"}), 400
        
        # Vérifier que le type de prompt est valide
        if prompt_type not in ['generation', 'evaluation']:
            return jsonify({"success": False, "error": "Type de prompt invalide"}), 400
        
        # Construire le prompt final en remplaçant les variables
        final_prompt = prompt_content
        
        if prompt_type == 'generation':
            niveau = params.get('niveau', 'Terminale')
            theme = params.get('theme', 'Algorithmes')
            difficulte = params.get('difficulte', 3)
            description = params.get('description', 'Exercice sur les algorithmes')
            debutant = params.get('debutant', False)
            
            # Créer le niveau_python en fonction de debutant
            niveau_python = ""
            if debutant:
                niveau_python = """
IMPORTANT: Cet exercice est destiné à des débutants en Python. 
N'utilise PAS de fonctions, de classes, d'objets ou d'autres concepts avancés dans le squelette de code.
Utilise uniquement des variables, des opérations de base, des conditions (if/else) et des boucles (for/while).
Le code doit être simple et direct, sans abstractions avancées.
"""
            else:
                niveau_python = """
Cet exercice peut utiliser des fonctions, des classes et d'autres concepts avancés de Python si nécessaire.
"""
            
            # Remplacer les variables dans le prompt
            final_prompt = final_prompt.replace('{niveau}', niveau)
            final_prompt = final_prompt.replace('{theme}', theme)
            final_prompt = final_prompt.replace('{difficulte}', str(difficulte))
            final_prompt = final_prompt.replace('{description}', description)
            final_prompt = final_prompt.replace('{debutant}', str(debutant).lower())
            final_prompt = final_prompt.replace('{niveau_python}', niveau_python)
        
        elif prompt_type == 'evaluation':
            code = params.get('code', '# Code à évaluer')
            enonce = params.get('enonce', 'Énoncé de l\'exercice')
            html_formatting = params.get('HTML_FORMATTING_INSTRUCTIONS', HTML_FORMATTING_INSTRUCTIONS)
            
            # Remplacer les variables dans le prompt
            final_prompt = final_prompt.replace('{code}', code)
            final_prompt = final_prompt.replace('{enonce}', enonce)
            final_prompt = final_prompt.replace('{HTML_FORMATTING_INSTRUCTIONS}', html_formatting)
        
        # Utiliser l'IA pour générer une réponse
        try:
            response = generate_text(final_prompt, max_tokens=1024, temperature=0.7)
            
            # Convertir la réponse en HTML pour l'affichage
            if prompt_type == 'generation':
                import markdown
                response_html = markdown.markdown(response)
            else:
                response_html = response
            
            return jsonify({
                "success": True,
                "prompt": final_prompt,
                "response": response_html
            })
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la génération du texte: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Erreur lors de la génération du texte: {str(e)}"
            }), 500
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du test du prompt: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Nettoyage périodique des fichiers temporaires
@exercise_bp.route('/api/cleanup_temp_data')
def cleanup_temp_data():
    """Nettoie les fichiers temporaires plus anciens que 1 heure"""
    try:
        current_time = time.time()
        scripts_deleted = 0
        notebooks_deleted = 0
        
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > 3600:
                try:
                    os.remove(file_path)
                    if filename.endswith('.py'):
                        scripts_deleted += 1
                    elif filename.endswith('.ipynb'):
                        notebooks_deleted += 1
                except:
                    pass
            
        return jsonify({
            "success": True, 
            "scripts_deleted": scripts_deleted,
            "notebooks_deleted": notebooks_deleted
        })
    except Exception as e:
        return jsonify({"error": str(e)})
