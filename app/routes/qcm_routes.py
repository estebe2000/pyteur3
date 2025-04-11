from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from app import csrf
import os
import glob
import json
from werkzeug.utils import secure_filename

qcm_bp = Blueprint('qcm', __name__)

@qcm_bp.route('/qcm_flash')
@login_required
def qcm_flash():
    # Vérifier si la requête vient d'un iframe
    is_iframe = request.args.get('iframe', 'false') == 'true'
    
    # Récupérer les labels pour le titre
    from app.lang.lang_fr import LABELS as labels_fr
    from app.lang.lang_en import LABELS as labels_en
    lang = request.cookies.get('lang', 'fr')
    labels = labels_fr if lang == 'fr' else labels_en
    
    # Structure des niveaux et thèmes disponibles
    themes = {
        'snt': [
            {'name': 'Internet', 'file': 'internet'},
            {'name': 'Web', 'file': 'web'},
            {'name': 'Réseaux sociaux', 'file': 'rs'},
            {'name': 'Données structurées', 'file': 'donnees'},
            {'name': 'Localisation', 'file': 'carto'},
            {'name': 'Photo numérique', 'file': 'photos'},
            {'name': 'Informatique embarquée', 'file': 'embarque'}
        ],
        'nsi1': [
            {'name': 'Représentation des données', 'file': 'donnee'},
            {'name': 'Traitement des données', 'file': 'table'},
            {'name': 'Interactions Homme-Machine', 'file': 'ihm'},
            {'name': 'Architectures matérielles', 'file': 'os'},
            {'name': 'Langages et programmation', 'file': 'language'},
            {'name': 'Algorithmique', 'file': 'algo'},
            {'name': 'Bases de données', 'file': 'base'},
            {'name': "Histoire de l'informatique", 'file': 'histoire'}
        ],
        'nsit': [
            {'name': 'Structures de données', 'file': 'structure'},
            {'name': 'Bases de données', 'file': 'base_de_donnee'},
            {'name': 'Architectures matérielles', 'file': 'os_lan'},
            {'name': 'Langages et programmation', 'file': 'language'},
            {'name': 'Algorithmique', 'file': 'algo'}
        ]
    }

    if is_iframe:
        return render_template('qcm_flash.html', 
                            title=labels.get('qcm_flash', 'QCM Flash'),
                            themes=themes)
    else:
        return render_template('qcm_flash.html',
                            themes=themes)

@qcm_bp.route('/qcm')
@login_required
def qcm():
    if current_user.role == 'eleve':
        return "Accès non autorisé", 403

    base_dir = os.path.join('app', 'static', 'data', 'qcm')
    pattern = os.path.join(base_dir, '**', '*.json')
    files = glob.glob(pattern, recursive=True)
    qcm_files = [os.path.relpath(f, base_dir).replace('\\', '/') for f in files]

    saved_dir = os.path.join('app', 'static', 'uploads', 'qcm')
    saved_pattern = os.path.join(saved_dir, '*.json')
    saved_files = glob.glob(saved_pattern)
    saved_qcms = [os.path.basename(f) for f in saved_files]

    return render_template('qcm.html', qcm_files=qcm_files, saved_qcms=saved_qcms)

@qcm_bp.route('/get_saved_qcms')
@login_required
def get_saved_qcms():
    """Retourne la liste des QCM sauvegardés avec leurs métadonnées"""
    saved_dir = os.path.join('app', 'static', 'uploads', 'qcm')
    saved_files = glob.glob(os.path.join(saved_dir, '*.json'))
    
    qcms = []
    for filepath in saved_files:
        filename = os.path.basename(filepath)
        stat = os.stat(filepath)
        qcms.append({
            'name': filename.replace('.json', ''),
            'date': stat.st_mtime * 1000,  # timestamp en ms
            'code': filename.replace('.json', '')
        })
    
    return jsonify(qcms)

@csrf.exempt
@qcm_bp.route('/save_qcm', methods=['POST'])
@login_required
def save_qcm():
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

@csrf.exempt
@qcm_bp.route('/delete_qcm/<code>', methods=['DELETE'])
@login_required
def delete_qcm(code):
    try:
        if current_user.role == 'eleve':
            return "Accès non autorisé", 403
            
        # Vérifier que le code est valide (alphanumérique)
        if not code.isalnum():
            return "Code QCM invalide", 400
            
        filename = secure_filename(code) + '.json'
        uploads_dir = os.path.join('app', 'static', 'uploads', 'qcm')
        filepath = os.path.join(uploads_dir, filename)
        
        # Vérifier que le chemin est bien dans le répertoire autorisé
        if not os.path.abspath(filepath).startswith(os.path.abspath(uploads_dir)):
            return "Chemin non autorisé", 403
            
        if not os.path.exists(filepath):
            return "QCM non trouvé", 404
            
        os.remove(filepath)
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
