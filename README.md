# Pyteur - Plateforme éducative interactive

![Licence MIT](https://img.shields.io/badge/Licence-MIT-green)

## Description
Pyteur est une plateforme web éducative développée avec Flask.  
Elle permet la gestion d'utilisateurs, la gestion de classes et groupes, l'upload sécurisé de documents PDF, la gestion et l'exécution d'exercices multi-langages, et intègre un bac à sable interactif multi-langages (Python, SQL, OCaml, JavaScript, Xcas) via Basthon Console et Notebook.

## Nouveautés UX
- **Page de connexion immersive** avec :
  - Faux terminal Python animé simulant une console interactive
  - Logo Pyteur animé calmement
- **Interface moderne et responsive** avec Tailwind CSS + Bootstrap
- **Boutons uniformisés** pour une expérience utilisateur cohérente

## Fonctionnalités principales
- Authentification sécurisée (Flask-Login + CSRF)
- Gestion des utilisateurs avec rôles (admin, professeur, élève)
- Gestion des classes et groupes d'élèves
- Suppression d'une classe supprime automatiquement tous ses groupes associés
- Upload et gestion de documents PDF (limité aux fichiers PDF)
- Gestion et exécution d'exercices multi-langages (Python, SQL, OCaml, JavaScript, Xcas)
- Bac à sable interactif multi-langages (console et notebook)
- Interface responsive compatible mobile et desktop
- Fil d'Ariane pour la navigation
- Sidebar dynamique avec menu mobile
- Affichage dynamique de l'heure

## Installation locale (sans Docker)

1. **Cloner le dépôt**
```bash
git clone https://github.com/votre-utilisateur/pyteur.git
cd pyteur
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
# Sous Linux/macOS
source .venv/bin/activate
# Sous Windows
.venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine avec :

```
SECRET_KEY=your_secret_key
```

5. **Initialiser ou réinitialiser la base de données**

- Pour initialiser :
```bash
python manage.py --init
```

- Pour réinitialiser (supprimer + recréer) :
```bash
python manage.py --reset --init
```

Ce script crée automatiquement trois comptes :

| Rôle           | Email                | Mot de passe |
|----------------|----------------------|--------------|
| Administrateur | admin@pyteur.com     | admin        |
| Professeur     | prof@pyteur.com      | prof         |
| Élève          | eleve@pyteur.com     | eleve        |

6. **Lancer l'application**
```bash
python run.py
```

L'application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Lancement avec Docker

### Prérequis
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Commandes

1. **Construire et lancer les conteneurs**
```bash
docker-compose up --build
```

2. **Réinitialiser la base de données (optionnel)**

Par défaut, la base n'est pas supprimée.  
Pour forcer la suppression + recréation au démarrage, éditez `docker-compose.yml` :

```yaml
environment:
  - RESET_DB=true
```

puis relancez :

```bash
docker-compose down
docker-compose up --build
```

L'application sera accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Structure du projet
```
├── app/                    # Code source Flask
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   ├── static/
│   └── templates/
├── Dockerfile              # Image Docker de l'app
├── docker-compose.yml      # Orchestration multi-conteneurs
├── manage.py               # Script init/reset base
├── init_db.py              # Init base
├── init_admin.py           # Création comptes admin
├── run.py                  # Lancement Flask
├── requirements.txt        # Dépendances Python
├── README.md
```

## Contribuer

Les contributions sont les bienvenues !

1. Forkez ce dépôt
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commitez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Poussez la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

## Sécurité

⚠️ Cette application est conçue pour un usage en environnement de développement ou éducatif.  
Pour un déploiement en production, pensez à :
- Configurer un serveur web sécurisé (ex: Nginx)
- Utiliser une base de données robuste (PostgreSQL, MySQL)
- Gérer les clés secrètes et variables sensibles de manière sécurisée
- Activer HTTPS
- Renforcer la gestion des permissions

## Crédits
- [Basthon](https://basthon.fr/) pour l'intégration console et notebook
- [Flask](https://flask.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Bootstrap](https://getbootstrap.com/)

---

## Licence
Ce projet est distribué sous licence MIT.
