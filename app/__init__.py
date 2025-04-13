
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'user.login'

    # Importer et enregistrer les blueprints
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.user_routes import user_bp
    from app.routes.document_routes import document_bp
    from app.routes.exercise_routes import exercise_bp
    from app.routes.messagerie_routes import messagerie_bp
    from app.routes.qcm_routes import qcm_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.misc_routes import misc_bp
    from app.routes.statistics_routes import statistics_bp
    from app.routes.eleve_routes import eleve_bp
    from app.routes.project_routes import project_bp
    from app.routes.welcome_routes import welcome_bp
    from app.routes.student_performance_routes import student_performance_bp
    from app.routes.debug_routes import debug_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(messagerie_bp)
    app.register_blueprint(qcm_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(misc_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(eleve_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(welcome_bp)
    app.register_blueprint(student_performance_bp)
    app.register_blueprint(debug_bp)

    @app.context_processor
    def inject_labels():
        from flask import session, request
        # Récupérer la langue depuis les cookies ou la session
        lang_code = request.cookies.get('lang') or session.get('lang', 'fr')
        if lang_code == 'en':
            try:
                from app.lang.lang_en import LABELS as LABELS_EN
                return {'labels': LABELS_EN}
            except ImportError:
                from app.lang.lang_fr import LABELS as LABELS_FR
                return {'labels': LABELS_FR}
        else:
            from app.lang.lang_fr import LABELS as LABELS_FR
            return {'labels': LABELS_FR}

    @app.context_processor
    def inject_menu_config():
        import os
        try:
            config_path = os.path.join(app.root_path, 'menu_config.json')
            print(f"[DEBUG] Chargement menu_config depuis : {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                menu_config = json.load(f)
            print(f"[DEBUG] menu_config chargé : {menu_config}")
        except Exception as e:
            print(f"[DEBUG] Erreur chargement menu_config : {e}")
            menu_config = {}
        return {'menu_config': menu_config}

    @app.context_processor
    def inject_drive_url():
        import os
        try:
            config_path = os.path.join(app.root_path, 'drive_config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            drive_url = config_data.get('drive_url', 'https://nuage.apps.education.fr/')
        except Exception:
            drive_url = 'https://nuage.apps.education.fr/'
        return {'drive_url': drive_url}

    # Ajouter un filtre Jinja2 pour charger les fichiers JSON
    @app.template_filter('load_json')
    def load_json_filter(path):
        import os
        try:
            full_path = os.path.join(app.root_path, path)
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier JSON {path}: {e}")
            return {}

    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
