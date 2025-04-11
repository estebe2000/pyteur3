from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app, send_file, flash
from flask_login import current_user
import os
import json
import uuid
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from app.models import db, User, Document, SchoolClass, ExerciseAssignment
from app.ia_client import generate_text
from app.prompts_generateur import prompt_generation_exercice
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
            current_app.logger.error(f"Erreur lors de la génération du texte: {str(e)}")
            response = f"L'IA n'est pas disponible actuellement. Voici l'énoncé de l'exercice:\n\n# Exercice sur {theme}\n\nNiveau: {niveau}, Difficulté: {difficulte}/5\n\n{description}\n\n```python\n# Votre code ici\n```"
        
        current_app.logger.info("Envoi de la réponse au client")
        return jsonify({"prompt": prompt, "response": response})
    except Exception as e:
        current_app.logger.error(f"Erreur dans generer_exercice: {str(e)}")
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
    # Récupérer tous les exercices
    exercises = Document.query.filter_by(type='exercise').all()
    return render_template('exercises.html', exercises=exercises)

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
            
            # Créer un nom de fichier unique
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Créer le répertoire s'il n'existe pas
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Enregistrer le fichier
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Récupérer les tags
            tags = request.form.get('tags', '')
            
            # Créer un document dans la base de données
            document = Document(
                filename=unique_filename,
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
            
            # Créer un nom de fichier unique
            filename = f"{uuid.uuid4()}.py"
            
            # Créer le répertoire s'il n'existe pas
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Enregistrer le fichier
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Récupérer les tags
            tags = request.form.get('tags', '')
            
            # Créer un document dans la base de données
            document = Document(
                filename=filename,
                original_filename=filename,
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

@exercise_bp.route('/assign_exercise/<int:exercise_id>')
def assign_exercise(exercise_id):
    """Affecter un exercice à des élèves"""
    exercise = Document.query.get_or_404(exercise_id)
    classes = SchoolClass.query.all()
    return render_template('assign_exercise.html', exercise=exercise, classes=classes)

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
