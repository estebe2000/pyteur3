from app import create_app, db
from app.models import User, SchoolClass, Group
from werkzeug.security import generate_password_hash
from datetime import date

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
        
        # Suppression de l'élève par défaut pour éviter la duplication
        default_eleve = User.query.filter_by(login='eleve').first()
        if default_eleve:
            db.session.delete(default_eleve)
            print("Élève par défaut supprimé pour éviter la duplication")
        
        db.session.commit()
        print("Base de données initialisée avec les comptes par défaut")
        
        # Création de la classe "classe pyteur"
        existing_class = SchoolClass.query.filter_by(nom="pyteur").first()
        if not existing_class:
            school_class = SchoolClass(
                nom="pyteur",
                niveau="Terminale"
            )
            db.session.add(school_class)
            db.session.commit()
            print(f"Classe 'classe pyteur' créée avec l'ID: {school_class.id}")
        else:
            school_class = existing_class
            print("La classe 'classe pyteur' existe déjà.")
        
        # Création du groupe "groupe pyteur" dans cette classe
        existing_group = Group.query.filter_by(nom="groupe pyteur", class_id=school_class.id).first()
        if not existing_group:
            group = Group(
                nom="groupe pyteur",
                class_id=school_class.id
            )
            db.session.add(group)
            db.session.commit()
            print(f"Groupe 'groupe pyteur' créé avec l'ID: {group.id}")
        else:
            group = existing_group
            print("Le groupe 'groupe pyteur' existe déjà.")
        
        # Création de l'élève "eleve pyteur" et ajout au groupe
        existing_user = User.query.filter_by(login="eleve.pyteur").first()
        if not existing_user:
            user = User(
                nom="Pyteur",
                prenom="Eleve",
                login="eleve",
                password=generate_password_hash("eleve"),
                role="eleve",
                date_naissance=date(2005, 1, 1),
                sexe="G",
                email="eleve.pyteur@example.com",
                class_id=school_class.id,
                group_id=group.id
            )
            db.session.add(user)
            db.session.commit()
            print(f"Élève 'eleve pyteur' créé avec l'ID: {user.id}")
        else:
            print("L'utilisateur 'eleve pyteur' existe déjà.")
