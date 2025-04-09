# Pyteur - Plateforme éducative interactive

![Licence MIT](https://img.shields.io/badge/Licence-MIT-green)

## Description
Pyteur est une plateforme web éducative développée avec Flask.  
Elle permet la gestion d'utilisateurs, la gestion de classes et groupes, l'upload sécurisé de documents PDF, la gestion et l'exécution d'exercices multi-langages, et intègre un bac à sable interactif multi-langages (Python, SQL, OCaml, JavaScript, Xcas) via Basthon Console et Notebook.  
Elle propose également des fonctionnalités d'intelligence artificielle pour générer ou corriger des exercices.

---

## Nouveautés UX
- **Page de connexion immersive** avec :
  - Faux terminal Python animé simulant une console interactive
  - Logo Pyteur animé calmement
- **Interface moderne et responsive** avec Tailwind CSS + Bootstrap
- **Boutons uniformisés** pour une expérience utilisateur cohérente

---

## Fonctionnalités principales
- Authentification sécurisée (Flask-Login + CSRF)
- Gestion des utilisateurs avec rôles (admin, professeur, élève)
- Gestion des classes et groupes d'élèves
- Suppression d'une classe supprime automatiquement tous ses groupes associés
- Upload et gestion de documents PDF (limité aux fichiers PDF)
- Gestion et exécution d'exercices multi-langages (Python, SQL, OCaml, JavaScript, Xcas)
- Bac à sable interactif multi-langages (console et notebook)
- Intégration d'IA pour la génération et correction d'exercices
- Interface responsive compatible mobile et desktop
- Fil d'Ariane pour la navigation
- Sidebar dynamique avec menu mobile
- Affichage dynamique de l'heure

---

## Fonctionnalités IA
- Intégration avec plusieurs fournisseurs d'IA configurables (OpenAI, Mistral, etc.)
- Génération automatique d'exercices à partir de consignes
- Correction automatique d'exercices soumis par les élèves
- Configuration flexible via fichiers `app/ia_config.json` et `app/ia_providers.json`
- Gestion des fournisseurs IA via l'interface d'administration

---

## Technologies utilisées
- **Backend** : Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Base de données** : SQLite (par défaut)
- **Frontend** : HTML5, Tailwind CSS, Bootstrap, JavaScript
- **Bac à sable multi-langages** : [Basthon](https://basthon.fr)
- **Intelligence Artificielle** : OpenAI, Mistral AI
- **Conteneurisation** : Docker, Docker Compose
- **Autres** : python-dotenv, requests, gunicorn (optionnel)

---

## Structure du projet

```
pyteur3/
├── app.py                 # Point d'entrée Flask
├── run.py                 # Lancement de l'application
├── manage.py              # Scripts init/reset base de données
├── config.py              # Configuration Flask
├── models.py              # Modèles SQLAlchemy
├── mistral_client.py      # Client API Mistral
├── init_db.py             # Initialisation base
├── init_admin.py          # Création comptes par défaut
├── requirements.txt       # Dépendances Python
├── Dockerfile             # Image Docker
├── docker-compose.yml     # Orchestration Docker
├── app/
│   ├── __init__.py        # Initialisation app Flask
│   ├── routes/            # Routes Flask
│   ├── lang/              # Fichiers de langue
│   ├── static/            # Fichiers statiques (css, js, images)
│   └── templates/         # Templates HTML Jinja2
└── README.md              # Documentation
```

---

## Installation locale (sans Docker)

1. **Cloner le dépôt**
```bash
git clone https://github.com/estebe2000/pyteur3.git
cd pyteur3
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

Créer un fichier `.env` à la racine avec au minimum :

```
SECRET_KEY=your_secret_key
```

### Configuration avancée (.env)

Vous pouvez également définir d'autres variables selon vos besoins :

```
# Clé secrète Flask
SECRET_KEY=your_secret_key

# Clé API pour un fournisseur IA par défaut
IA_API_KEY=your_api_key

# URL du serveur IA personnalisé
IA_API_URL=https://api.monfournisseur.com

# Forcer le reset de la base au démarrage (utile en dev)
RESET_DB=true
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

| Rôle           | Login                | Mot de passe |
|----------------|----------------------|--------------|
| Administrateur | admin                | admin        |
| Professeur     | prof                 | prof         |
| Élève          | eleve                | eleve        |

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

### Installation optionnelle d'Ollama

Par défaut, Ollama **n'est pas installé** dans l'image Docker.  
Pour installer Ollama lors de la construction, ajoutez l'argument `INSTALL_OLLAMA=true` à la commande `docker build` :

```bash
docker build --build-arg INSTALL_OLLAMA=true -t nom_image .
```

Puis lancez le conteneur avec cette image :

```bash
docker run -p 5000:5000 nom_image
```

Avec `docker-compose`, vous pouvez aussi passer cet argument en modifiant votre `docker-compose.yml` :

```yaml
services:
  votre_service:
    build:
      context: .
      args:
        INSTALL_OLLAMA: "true"
```

2. **Réinitialiser la base de données (optionnel)**

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

## Scripts utilitaires

- `manage.py` : initialisation et réinitialisation de la base de données
- `init_db.py` : script d'initialisation de la base
- `init_admin.py` : création des comptes administrateur, professeur, élève par défaut
- `reset.sh` / `reset.bat` : scripts shell/batch pour réinitialiser rapidement l'environnement
- `ollama_entrypoint.sh` : script d'initialisation pour Ollama dans Docker

---

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

---

## Auteurs

- **Estebe2000** (https://github.com/estebe2000)
- Contributions bienvenues via pull requests.
