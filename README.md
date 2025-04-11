# Pyteur

**Pyteur** est une plateforme éducative collaborative open-source, conçue pour les enseignants et élèves, intégrant la génération d’exercices assistée par IA, la gestion de classes, la messagerie, le suivi pédagogique et des outils interactifs.  
Ce projet est développé pour l’Éducation Nationale française, sous licence **MIT**.

---

## Fonctionnalités principales

- **Gestion des utilisateurs** (élèves, professeurs, administrateurs)
- **Gestion des classes et groupes**
- **Messagerie interne** avec interface fenêtrée
- **Gestion documentaire** (import/export, affectation) avec limite de taille
- **Création et génération d’exercices assistée par IA**
- **QCM interactifs** et **QCM flash** (mode rapide)
- **Suivi personnalisé des élèves** avec statistiques détaillées
- **Tableau de bord** avec widgets personnalisables
- **Support multi-langues** (français, anglais)
- **Importation d’utilisateurs** via CSV
- **Gestion des fournisseurs IA** (Ollama, autres)
- **Interface moderne** avec :
  - Sections repliables
  - Graphiques dynamiques (Chart.js)
  - Mode fenêtré pour les élèves
  - Thème sombre/clair

---

## Structure du projet (simplifiée)

```
├── app/
│   ├── __init__.py             # Configuration Flask
│   ├── routes/                 # 12 blueprints (utilisateurs, QCM, IA, etc.)
│   ├── models.py               # Modèles SQLAlchemy
│   ├── ia_client.py            # Client IA avec cache
│   ├── prompts_generateur.py   # Prompts IA optimisés
│   ├── static/
│   │   ├── css/                # CSS (Bootstrap + Tailwind)
│   │   ├── js/                 # JavaScript (jQuery, Chart.js, DataTables)
│   │   ├── basthon/            # Intégration Basthon
│   │   └── uploads/            # Fichiers utilisateurs avec quotas
│   ├── templates/
│   │   ├── eleve_windows/      # Interface fenêtrée élève
│   │   └── ...                 # 30+ templates
│   ├── lang/                   # Internationalisation
│   └── *.json                  # Configurations (menu, drive)
│
├── docker/                     # Fichiers Docker
├── scripts/                    # Scripts utilitaires
├── tests/                      # Tests unitaires
└── *.py                        # Scripts principaux
```

---

## Installation rapide

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

5. **Lancer l’application**

```bash
python run.py
```

---

## Configuration

Les paramètres principaux sont configurés dans `config.py` :

```python
# Configuration de base
SECRET_KEY = 'dev_secret_key'  # À remplacer en production
SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/db.sqlite'  # SQLite par défaut

# Variables d'environnement prioritaires
# export DATABASE_URL=postgresql://user:pass@localhost/dbname
# export SECRET_KEY=votre_clé_secrète
```

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

Configuration disponible dans `docker-compose.yml` (développement) ou `docker-compose-gunicorn.yml` (production):
- Service principal `pyteur_os` sur le port 5000 (dev) ou 5001 (prod)
- Service `ollama` pour l'IA locale (port 11434)
- Variables d'environnement configurables:
  ```yaml
  environment:
    - FLASK_ENV=development|production
    - RESET_DB=true|false
    - SECRET_KEY=votre_clé_secrète
    - DATABASE_URL=postgresql://user:pass@host/dbname
  ```

### Déploiement avec Gunicorn (sans Docker)

Pour un déploiement en production sans Docker, utilisez les scripts fournis:

```bash
# Linux/Mac
./start_gunicorn.sh

# Windows
start_gunicorn.bat
```

Ces scripts démarrent l'application avec Gunicorn sur le port 5001, avec des paramètres optimisés définis dans `gunicorn_config.py`.

> **Notes importantes**:
> - Pour la production, configurez :
>   - `FLASK_ENV=production`
>   - Une base de données externe via `DATABASE_URL`
>   - Une `SECRET_KEY` robuste
> - Le volume `ollama_data` persiste les modèles IA entre les redémarrages
> - Le port 5001 est utilisé pour éviter les conflits avec d'autres services sur le port 5000

---

## Technologies utilisées

- **Python 3.10+**
- **Flask** (framework web)
- **SQLAlchemy** (ORM)
- **Bootstrap** et **Tailwind CSS** (design responsive)
- **FontAwesome** (icônes)
- **Chart.js** (graphiques dynamiques)
- **jQuery** (manipulation DOM)
- **DataTables** (tableaux interactifs)
- **Ollama** (API IA)
- **Basthon** (exécution Python dans le navigateur) : [https://basthon.fr](https://basthon.fr)

---

## État d'avancement

✅ **Fonctionnalités implémentées:**
- Gestion complète des utilisateurs et classes
- Messagerie avec notifications
- Système de documents avec quotas
- QCM standards et flash
- Tableau de bord professeur/élève
- Intégration Basthon et IA
- Internationalisation (fr/en)

🚧 **En développement:**
- Amélioration du système de défis
- Tableaux de bord avancés
- Export des données pédagogiques

💡 **Idées futures:**
- Intégration LTI
- Synchronisation avec Pronote
- Module de compétences

---

## Améliorations techniques

- **Sécurité:**
  - Validation des uploads
  - Politiques de mot de passe
  - Protection CSRF

- **Performance:**
  - Cache des requêtes IA
  - Optimisation des requêtes SQL
  - Chargement différé des assets

- **Évolutivité:**
  - Support PostgreSQL
  - Architecture modulaire
  - API REST

---

## Licence

Ce projet est open-source sous licence **MIT** et destiné à un usage pédagogique dans l’Éducation Nationale.

---
