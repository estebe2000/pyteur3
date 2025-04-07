from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Créer les utilisateurs par défaut
        if not User.query.filter_by(email='admin@pyteur.com').first():
            admin = User(
                email='admin@pyteur.com',
                password=generate_password_hash('admin', method='pbkdf2:sha256'),
                prenom='Admin',
                nom='Pyteur',
                login='admin',
                role='admin'
            )
            db.session.add(admin)
        
        if not User.query.filter_by(email='prof@pyteur.com').first():
            prof = User(
                email='prof@pyteur.com',
                password=generate_password_hash('prof', method='pbkdf2:sha256'),
                prenom='Professeur',
                nom='Pyteur',
                login='prof',
                role='professeur'
            )
            db.session.add(prof)
        
        if not User.query.filter_by(email='eleve@pyteur.com').first():
            eleve = User(
                email='eleve@pyteur.com',
                password=generate_password_hash('eleve', method='pbkdf2:sha256'),
                prenom='Élève',
                nom='Pyteur',
                login='eleve',
                role='eleve'
            )
            db.session.add(eleve)
        
        db.session.commit()
        print("Base de données initialisée avec les comptes par défaut")
