# Pyteur

**Pyteur** est une plateforme éducative collaborative open-source, conçue pour les enseignants et élèves, intégrant la génération d’exercices assistée par IA, la gestion de classes, la messagerie, le suivi pédagogique et des outils interactifs.  
Ce projet est développé pour l’Éducation Nationale française, sous licence **MIT**.

---

## Fonctionnalités principales

- **Gestion des utilisateurs** (élèves, professeurs, administrateurs)
- **Gestion des classes et groupes**
- **Messagerie interne**
- **Gestion documentaire** (import/export, affectation)
- **Création et génération d’exercices assistée par IA**
- **QCM interactifs**
- **Suivi personnalisé des élèves**
- **Tableau de bord et statistiques avancées**
- **Support multi-langues (français, anglais)**
- **Importation d’utilisateurs via CSV**
- **Gestion des fournisseurs IA (Ollama, autres)**
- **Refonte UX moderne avec sections repliables et graphiques dynamiques**

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
│   │   ├── data/               # Données JSON
│   │   └── js/                 # Scripts JavaScript (statistiques.js)
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

## Installation avec Docker

1. **Construire l’image**

```bash
docker build -t pyteur .
```

2. **Lancer avec Docker Compose**

```bash
docker-compose up
```

L’application sera accessible sur `http://localhost:5000`.

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

Ce projet est open-source sous licence **MIT** et destiné à un usage pédagogique dans l’Éducation Nationale.

---
