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
    login_manager.login_view = 'main.login'

    # Importer et enregistrer les blueprints ici plus tard
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

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

    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
