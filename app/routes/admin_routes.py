from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import csrf
import json
import os
import requests

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/gestion_menu', methods=['GET', 'POST'])
@login_required
def gestion_menu():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403

    config_path = 'app/menu_config.json'

    if request.method == 'POST':
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                menu_config = json.load(f)
        except Exception:
            menu_config = {}

        # S'assurer que external_links existe
        if 'external_links' not in menu_config:
            menu_config['external_links'] = {}

        # Mettre à jour la config selon les cases cochées pour les sections internes
        for key in list(menu_config.keys()):
            if key != 'external_links':
                menu_config[key] = f"visible_{key}" in request.form

        # Traiter les liens externes
        # Réinitialiser les liens externes
        menu_config['external_links'] = {}
        
        # Récupérer tous les IDs de liens
        link_ids = request.form.getlist('link_ids')
        
        # Pour chaque ID de lien, récupérer les données correspondantes
        for link_id in link_ids:
            name = request.form.get(f'link_name_{link_id}')
            url = request.form.get(f'link_url_{link_id}')
            icon = request.form.get(f'link_icon_{link_id}')
            target = request.form.get(f'link_target_{link_id}')
            visible = f'link_visible_{link_id}' in request.form
            
            # Vérifier que les données essentielles sont présentes
            if name and url:
                menu_config['external_links'][link_id] = {
                    'name': name,
                    'url': url,
                    'icon': icon or 'fa-globe',  # Icône par défaut
                    'target': target or 'window',  # Comportement par défaut
                    'visible': visible
                }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(menu_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            from flask import flash
            flash(f"Erreur lors de l'enregistrement de la configuration: {str(e)}", "error")

        from flask import redirect, url_for, flash
        flash("Configuration du menu enregistrée.", "success")
        return redirect(url_for('admin.gestion_menu'))

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            menu_config = json.load(f)
    except Exception:
        menu_config = {}
        
    # S'assurer que external_links existe
    if 'external_links' not in menu_config:
        menu_config['external_links'] = {}

    return render_template('gestion_menu.html', menu_config=menu_config)

@admin_bp.route('/manage_providers')
@login_required
def manage_providers():
    if current_user.role != 'admin':
        return "Accès non autorisé", 403
    try:
        with open('app/ia_providers.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        config_json = json.dumps(config, indent=4, ensure_ascii=False)
    except Exception as e:
        config_json = f"Erreur chargement config: {str(e)}"
    return render_template('manage_providers.html', config_json=config_json)

@admin_bp.route('/api/ia_providers', methods=['GET'])
@login_required
def api_list_providers():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    try:
        with open('app/ia_providers.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/ia_providers', methods=['POST'])
@login_required
def api_add_provider():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    data = request.get_json()
    name = data.get('name')
    params = data.get('params')
    if not name or not params:
        return jsonify({'error': 'Nom ou paramètres manquants'}), 400
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name in config['providers']:
                return jsonify({'error': 'Nom déjà utilisé'}), 400
            config['providers'][name] = params
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/ia_providers/<name>', methods=['PUT'])
@login_required
def api_update_provider(name):
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    data = request.get_json()
    params = data.get('params')
    if not params:
        return jsonify({'error': 'Paramètres manquants'}), 400
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name not in config['providers']:
                return jsonify({'error': 'Fournisseur inexistant'}), 404
            config['providers'][name] = params
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/ia_providers/<name>', methods=['DELETE'])
@login_required
def api_delete_provider(name):
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name not in config['providers']:
                return jsonify({'error': 'Fournisseur inexistant'}), 404
            del config['providers'][name]
            if config.get('active_provider') == name:
                config['active_provider'] = None
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/ia_providers/activate/<name>', methods=['POST'])
@login_required
def api_activate_provider(name):
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    try:
        with open('app/ia_providers.json', 'r+', encoding='utf-8') as f:
            config = json.load(f)
            if name not in config['providers']:
                return jsonify({'error': 'Fournisseur inexistant'}), 404
            config['active_provider'] = name
            f.seek(0)
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.truncate()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/ollama_models', methods=['GET'])
@login_required
def api_ollama_models():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    try:
        url = 'http://localhost:11434'
        if os.path.exists('app/ia_config.json'):
            with open('app/ia_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config.get('ollama', {}).get('url', url)
        response = requests.get(url.rstrip('/') + '/v1/models', timeout=5)
        if response.status_code != 200:
            return jsonify({'error': f'Status {response.status_code}'}), 500
        data = response.json()
        models = [m['id'] for m in data.get('data', [])]
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/ollama_status', methods=['GET'])
@login_required
def api_ollama_status():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    try:
        url = 'http://localhost:11434'
        if os.path.exists('app/ia_config.json'):
            with open('app/ia_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config.get('ollama', {}).get('url', url)
        response = requests.get(url.rstrip('/') + '/v1/models', timeout=3)
        if response.status_code != 200:
            return jsonify({'installed': False, 'models': []})
        data = response.json()
        models = [m['id'] for m in data.get('data', [])]
        return jsonify({'installed': True, 'models': models})
    except Exception:
        return jsonify({'installed': False, 'models': []})

@admin_bp.route('/api/ollama_pull', methods=['POST'])
@login_required
def api_ollama_pull():
    if current_user.role != 'admin':
        return {'error': 'Accès refusé'}, 403
    try:
        data = request.get_json(force=True)
        model_name = data.get('model_name')
        if not model_name:
            return {'error': 'Nom du modèle manquant'}, 400
        from app.ollama_api import pull_model
        pull_model(model_name)
        return {'success': True}
    except Exception as e:
        return {'error': str(e)}, 500

@admin_bp.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    # Tous les utilisateurs authentifiés peuvent utiliser le chat IA
    try:
        data = request.get_json(force=True)
        message = data.get('message')
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Utiliser le client IA pour générer une réponse
        from app.ia_client import generate_text
        response = generate_text(message)
        
        # Si la réponse est vide ou trop courte, ajouter un message d'erreur
        if not response or len(response) < 5:
            return jsonify({'error': 'Aucune réponse générée. Vérifiez la configuration de l\'IA.'}), 500
        
        return jsonify({'response': response})
    except ImportError:
        # Si le module ia_client n'existe pas ou si la fonction generate_text n'est pas disponible
        return jsonify({'error': 'Module IA non disponible. Vérifiez l\'installation.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/save_ia_config', methods=['POST'])
@login_required
def api_save_ia_config():
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403
    try:
        data = request.get_json(force=True)
        if not isinstance(data, dict) or not data:
            return jsonify({'error': 'JSON vide ou invalide'}), 400

        if os.path.exists('app/ia_config.json'):
            with open('app/ia_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}

        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and isinstance(d.get(k), dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v

        deep_update(config, data)

        with open('app/ia_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
