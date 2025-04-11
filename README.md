# 📚 PYTEUR OS

**Pyteur OS** est une plateforme éducative collaborative open-source conçue pour l'Éducation Nationale française. Développée dans le cadre d'un projet universitaire (Licence 3), cette solution intègre la génération d'exercices assistée par IA, la gestion de classes, la messagerie, le suivi pédagogique et des outils interactifs pour créer un environnement d'apprentissage complet.

![Licence MIT](https://img.shields.io/badge/Licence-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.2+-lightgrey.svg)

## 🚀 Fonctionnalités principales

- **👥 Gestion des utilisateurs** - Élèves, professeurs, administrateurs avec rôles et permissions
- **🏫 Gestion des classes et groupes** - Organisation pédagogique flexible
- **💬 Messagerie interne** - Communication sécurisée avec interface fenêtrée
- **📂 Gestion documentaire** - Import/export, affectation avec limite de taille
- **✍️ Création d'exercices assistée par IA** - Génération automatique de contenu pédagogique
- **📝 QCM interactifs** - Mode standard et flash (rapide)
- **📊 Suivi personnalisé des élèves** - Statistiques détaillées et recommandations
- **📱 Interface moderne** - Responsive, thème clair/sombre, mode fenêtré pour les élèves
- **🌐 Support multilingue** - Français et anglais
- **📋 Importation d'utilisateurs** - Via fichiers CSV
- **🤖 Intégration IA** - Support pour Ollama et autres fournisseurs

## 🛠️ Technologies utilisées

- **Backend**
  - Python 3.10+
  - Flask (framework web)
  - SQLAlchemy (ORM)
  - Flask-Login (authentification)
  - Flask-WTF (formulaires et CSRF)
  - Gunicorn (serveur WSGI production)

- **Frontend**
  - Bootstrap et Tailwind CSS (design responsive)
  - JavaScript / jQuery
  - Chart.js (graphiques dynamiques)
  - DataTables (tableaux interactifs)
  - FontAwesome (icônes)

- **IA et Intégrations**
  - Ollama (IA locale)
  - API Mistral (option cloud)
  - Basthon (exécution Python dans le navigateur)

- **Déploiement**
  - Docker / Docker Compose
  - Gunicorn (serveur WSGI)
  - Scripts d'automatisation (systemd, batch)

## 📋 Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Docker et Docker Compose (optionnel, pour déploiement conteneurisé)
- Navigateur web moderne (Chrome, Firefox, Edge, Safari)
- 2 Go RAM minimum (4 Go recommandés)
- 1 Go d'espace disque (hors modèles IA)

## 🔧 Installation

### Installation locale

1. **Cloner le dépôt**

```bash
git clone https://github.com/estebe2000/pyteur3.git
cd pyteur3
```

2. **Créer un environnement virtuel**

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sous Windows
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Initialiser la base de données**

```bash
python manage.py --init
```

5. **Lancer l'application**

```bash
python run.py
```

L'application sera accessible à l'adresse http://localhost:5000

### Comptes par défaut

L'application est préconfigurée avec trois comptes utilisateurs par défaut :

| Type de compte | Identifiant | Mot de passe |
|----------------|-------------|--------------|
| Administrateur | admin       | admin        |
| Professeur     | prof        | prof         |
| Élève          | eleve       | eleve        |

### Configuration d'Ollama

Si vous utilisez Ollama avec le projet via Docker, vous devez configurer l'URL d'Ollama comme suit :

```
http://ollama:11434
```

Cette URL doit être spécifiée dans les paramètres de configuration de l'IA dans l'interface d'administration.

### Installation avec Docker

#### Option 1: Construction manuelle
```bash
docker build -t pyteur .
docker run -p 5000:5000 pyteur
```

#### Option 2: Avec Docker Compose (développement)
```bash
docker-compose up
```

#### Option 3: Avec Docker Compose et Gunicorn (production recommandée)
```bash
docker-compose -f docker-compose-gunicorn.yml up
```

L'application sera accessible à l'adresse http://localhost:5001 (notez que le déploiement avec Gunicorn utilise le port 5001)

## 📁 Structure du projet

```
├── app/                        # Dossier principal de l'application
│   ├── __init__.py             # Configuration Flask
│   ├── routes/                 # Contrôleurs (12 blueprints)
│   ├── models.py               # Modèles SQLAlchemy
│   ├── ia_client.py            # Client IA avec cache
│   ├── static/                 # Ressources statiques
│   │   ├── css/                # Styles CSS
│   │   ├── js/                 # Scripts JavaScript
│   │   ├── basthon/            # Intégration Basthon
│   │   └── uploads/            # Fichiers utilisateurs
│   ├── templates/              # Templates Jinja2
│   │   ├── eleve_windows/      # Interface fenêtrée élève
│   │   └── ...                 # Autres templates
│   └── lang/                   # Internationalisation
├── docker-compose*.yml         # Configurations Docker
├── Dockerfile                  # Instructions de build Docker
├── gunicorn_config.py          # Configuration Gunicorn
├── manage.py                   # Script de gestion
├── requirements.txt            # Dépendances Python
├── run.py                      # Point d'entrée développement
└── wsgi.py                     # Point d'entrée production
```

## ⚙️ Configuration

Les paramètres principaux sont configurés dans `config.py` :

```python
# Configuration de base
SECRET_KEY = 'dev_secret_key'  # À remplacer en production
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/db.sqlite'  # SQLite par défaut

# Variables d'environnement prioritaires
# export DATABASE_URL=postgresql://user:pass@localhost/dbname
# export SECRET_KEY=votre_clé_secrète
```

## 🚀 Déploiement en production

### Avec Docker et démarrage automatique

Pour configurer le démarrage automatique des conteneurs Docker au démarrage du système:

**Sous Linux:**
1. Copiez le fichier `pyteur-docker.service` dans `/etc/systemd/system/`
2. Modifiez le chemin dans `WorkingDirectory=/path/to/pyteur3`
3. Activez et démarrez le service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pyteur-docker.service
   sudo systemctl start pyteur-docker.service
   ```

**Sous Windows:**
1. Copiez le fichier `pyteur-docker-autostart.bat` dans le dossier de démarrage:
   `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
2. Modifiez le chemin dans le script si nécessaire

### Sans Docker (avec Gunicorn)

Pour un déploiement en production sans Docker, utilisez les scripts fournis:

```bash
# Linux/Mac
./start_gunicorn.sh

# Windows
start_gunicorn.bat
```

## 📝 TODO

- [ ] **Sécurité**
  - [ ] Améliorer la validation des uploads
  - [ ] Renforcer les politiques de mot de passe
  - [ ] Ajouter l'authentification à deux facteurs

- [ ] **Performance**
  - [ ] Optimiser le cache des requêtes IA
  - [ ] Améliorer les requêtes SQL avec indexation
  - [ ] Implémenter le chargement différé des assets

- [ ] **Fonctionnalités**
  - [ ] Intégration LTI pour compatibilité ENT
  - [ ] Synchronisation avec Pronote
  - [ ] Module de compétences avancé
  - [ ] Export des données pédagogiques

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

## 👥 Auteurs et contributeurs

- **Équipe de développement L3 Informatique**
  - Université [Nom de l'université]
  - Promotion 2024-2025

## 🔗 Liens utiles

- [Documentation Flask](https://flask.palletsprojects.com/)
- [Documentation SQLAlchemy](https://docs.sqlalchemy.org/)
- [Basthon](https://basthon.fr/) - Exécution Python dans le navigateur
- [Ollama](https://ollama.ai/) - IA locale pour l'éducation

---

Développé avec ❤️ pour l'Éducation Nationale française
