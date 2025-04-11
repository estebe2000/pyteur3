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
    
    if is_iframe:
        return render_template('qcm_flash.html', title=labels.get('qcm_flash', 'QCM Flash'))
    else:
        return render_template('qcm_flash.html')

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
