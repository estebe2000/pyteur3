# ⚙️ Installation de Pyteur OS

![Installation Illustration](https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80)

Cette page vous guide pas à pas pour installer **Pyteur OS** sur votre ordinateur ou serveur, en local ou via Docker.

---

## 🖥️ Prérequis

- **Python** : 3.10 ou supérieur
- **pip** : gestionnaire de paquets Python
- **Docker** et **Docker Compose** (optionnel, recommandé pour la production)
- **Navigateur web** moderne (Chrome, Firefox, Edge, Safari)
- **Mémoire** : 2 Go RAM minimum (4 Go recommandé)
- **Espace disque** : 1 Go minimum (hors modèles IA)

---

## 🚀 Installation locale (développement)

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/estebe2000/pyteur3.git
   cd pyteur3
   ```
2. **Créer un environnement virtuel :**
   ```bash
   python -m venv .venv
   # Sous Windows :
   .venv\Scripts\activate
   # Sous Linux/Mac :
   source .venv/bin/activate
   ```
3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialiser la base de données :**
   ```bash
   python manage.py --init
   ```
5. **Lancer l’application :**
   ```bash
   python run.py
   ```
   Accès : [http://localhost:5000](http://localhost:5000)

---

## 🐳 Installation avec Docker

- **Construction manuelle :**
  ```bash
  docker build -t pyteur .
  docker run -p 5000:5000 pyteur
  ```
- **Avec Docker Compose (développement) :**
  ```bash
  docker-compose up
  ```
- **Avec Docker Compose + Gunicorn (production) :**
  ```bash
  docker-compose -f docker-compose-gunicorn.yml up
  ```
  Accès : [http://localhost:5001](http://localhost:5001)

---

## 🤖 Configuration IA (Ollama)

Si vous souhaitez utiliser l’IA (Ollama), configurez l’URL dans l’interface d’administration :
```
http://ollama:11434
```
> *Astuce : Ollama peut être lancé en local ou dans un conteneur Docker séparé.*

---

## 💡 Conseils

- Pour un usage en classe, privilégiez l’installation Docker pour l’isolation et la simplicité de déploiement.
- Pensez à sauvegarder régulièrement la base de données (fichier SQLite ou volume Docker).
- Consultez la [FAQ](faq) en cas de problème d’installation.

---

## 🔗 Ressources complémentaires

- [Dépôt GitHub Pyteur OS](https://github.com/estebe2000/pyteur3)
- [Documentation Docker](https://docs.docker.com/)
- [Ollama – IA locale](https://ollama.com/)

---
