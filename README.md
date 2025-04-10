# Pyteur

Plateforme éducative collaborative avec génération d’exercices assistée par IA.

---

## Fonctionnalités principales

- **Gestion des utilisateurs** (élèves, professeurs, administrateurs)
- **Gestion des classes et groupes**
- **Messagerie interne**
- **Gestion documentaire** (import/export, affectation)
- **Création et génération d’exercices assistée par IA**
- **QCM interactifs**
- **Suivi personnalisé des élèves**
- **Tableau de bord et statistiques**
- **Support multi-langues (français, anglais)**
- **Importation d’utilisateurs via CSV**
- **Gestion des fournisseurs IA (Ollama, autres)**

---

## Statistiques (UX améliorée)

- La page **Statistiques** est organisée en **blocs repliables** (Utilisateurs, Classes & Groupes, Exercices & Documents, Messagerie, ToDo Lists).
- Chaque bloc contient des **graphiques Chart.js** (2 par ligne max) et un **tableau interactif DataTables**.
- Le code JavaScript de chargement des données et création des graphiques est **externalisé dans** :

```
app/static/js/statistiques.js
```

- Pour personnaliser l’apparence, modifier le CSS dans :

```
app/templates/statistiques.html
```

- Pour adapter les données, modifier les routes API `/api/statistics/*` dans :

```
app/routes/statistics_routes.py
```

---

## Structure du projet

```
├── app/
│   ├── __init__.py
│   ├── routes/                 # Routes Flask
│   ├── models.py               # Modèles SQLAlchemy
│   ├── ia_client.py            # Client IA
│   ├── prompts_generateur.py   # Prompts IA
│   ├── ia_providers.py         # Gestion fournisseurs IA
│   ├── static/
│   │   ├── css/                # Feuilles de style
│   │   ├── img/                # Images
│   │   ├── uploads/            # Fichiers uploadés
│   │   └── data/               # Données JSON
│   ├── templates/              # Templates Jinja2
│   └── lang/                   # Fichiers de langue
│
├── manage.py                   # Script d'initialisation
├── init_db.py                  # Init base de données
├── init_admin.py               # Création comptes par défaut
├── run.py                      # Lancement serveur Flask
├── config.py                   # Configuration Flask
├── docker-compose.yml          # Docker Compose
├── Dockerfile                  # Dockerfile
├── requirements.txt            # Dépendances Python
└── README.md                   # Ce fichier
```

---

## Installation rapide

1. **Cloner le dépôt**

```bash
git clone <repo_url>
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

## Technologies

- **Python 3.10+**
- **Flask**
- **SQLAlchemy**
- **Bootstrap / Tailwind CSS**
- **FontAwesome**
- **Ollama / API IA**

---

## TODO

- [x] Gestion des utilisateurs
- [x] Gestion des classes et groupes
- [x] Messagerie interne
- [x] Gestion documentaire
- [x] Création et génération d’exercices assistée par IA
- [x] QCM interactifs
- [x] Support multi-langues
- [x] Importation CSV
- [x] Gestion des fournisseurs IA
- [x] Tableau de bord et statistiques
- [x] Refonte interface

### À faire

- [ ] Génération de QCM flash
- [ ] Suivi personnalisé avancé
- [ ] Finaliser la refonte interface (améliorations UI/UX)

---

## Licence

MIT
