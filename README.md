# Pyteur - Plateforme éducative interactive

![Licence MIT](https://img.shields.io/badge/Licence-MIT-green)

## Description
Pyteur est une plateforme web éducative développée avec Flask.  
Elle permet la gestion d'utilisateurs, la gestion de classes et groupes, l'upload sécurisé de documents PDF, la gestion et l'exécution d'exercices multi-langages, et intègre un bac à sable interactif multi-langages (Python, SQL, OCaml, JavaScript, Xcas) via Basthon Console et Notebook.  
Elle propose également des fonctionnalités d'intelligence artificielle pour générer ou corriger des exercices.

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
- Intégration d'IA pour la génération et correction d'exercices
- Interface responsive compatible mobile et desktop
- Fil d'Ariane pour la navigation
- Sidebar dynamique avec menu mobile
- Affichage dynamique de l'heure

## Fonctionnalités IA
- Intégration avec plusieurs fournisseurs d'IA configurables (OpenAI, Mistral, etc.)
- Génération automatique d'exercices à partir de consignes
- Correction automatique d'exercices soumis par les élèves
- Configuration flexible via fichiers `app/ia_config.json` et `app/ia_providers.json`
- Gestion des fournisseurs IA via l'interface d'administration

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

## Scripts utilitaires

- `manage.py` : initialisation et réinitialisation de la base de données
- `init_db.py` : script d'initialisation de la base
- `init_admin.py` : création des comptes administrateur, professeur, élève par défaut
- `reset
