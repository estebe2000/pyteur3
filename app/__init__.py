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

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(exercise_bp)
    app.register_blueprint(messagerie_bp)
    app.register_blueprint(qcm_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(misc_bp)

    @app.context_processor
    def inject_labels():
        from flask import session
        lang_code = session.get('lang', 'fr')
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

    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
