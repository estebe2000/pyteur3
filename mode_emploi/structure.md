# 🗂️ Structure du projet Pyteur OS

![Structure Illustration](https://images.unsplash.com/photo-1465101178521-c1a9136a3b41?auto=format&fit=crop&w=800&q=80)

Comprendre l’organisation du projet facilite la personnalisation, la maintenance et le développement de nouvelles fonctionnalités.

---

## 📁 Arborescence principale

```
pyteur3/
├── app/                        # Dossier principal de l'application
│   ├── __init__.py             # Configuration Flask
│   ├── routes/                 # Contrôleurs (blueprints)
│   ├── models.py               # Modèles SQLAlchemy
│   ├── ia_client.py            # Client IA
│   ├── static/                 # Ressources statiques (css, js, uploads)
│   ├── templates/              # Templates Jinja2 (pages)
│   └── lang/                   # Internationalisation
├── docker-compose*.yml         # Configurations Docker
├── Dockerfile                  # Instructions de build Docker
├── manage.py                   # Script de gestion
├── requirements.txt            # Dépendances Python
├── run.py                      # Point d'entrée développement
└── wsgi.py                     # Point d'entrée production
```

---

## 🗃️ Détail des dossiers/fichiers

- **app/** : cœur de l’application (code Python, templates, statiques…)
  - **routes/** : routes Flask (une par module/fonctionnalité)
  - **models.py** : modèles de données (SQLAlchemy)
  - **ia_client.py** : gestion de l’IA (Ollama, Mistral…)
  - **static/** : fichiers statiques (CSS, JS, images, uploads)
  - **templates/** : pages HTML (Jinja2)
  - **lang/** : fichiers de traduction (fr, en)
- **manage.py** : script de gestion (init, reset, etc.)
- **requirements.txt** : dépendances Python
- **run.py** : lancement en mode développement
- **wsgi.py** : lancement en production (Gunicorn)
- **Dockerfile** et **docker-compose*.yml** : déploiement Docker

---

## 🛠️ Conseils d’organisation

- Ne modifiez pas directement les fichiers du cœur (app/routes, app/models.py) sans sauvegarde.
- Placez vos images, scripts JS et CSS personnalisés dans `app/static/`.
- Ajoutez vos propres templates dans `app/templates/` si besoin.
- Utilisez le dossier `lang/` pour traduire ou adapter l’interface.

---

## 💡 Astuce

Pour ajouter une nouvelle fonctionnalité, créez un nouveau fichier dans `app/routes/` et un template associé dans `app/templates/`.

---
