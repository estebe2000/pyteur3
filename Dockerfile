# Utilise une image Python officielle
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Créer le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier le reste du code
COPY . .

# Exposer uniquement le port Gunicorn
EXPOSE 5001

# Commande de démarrage
CMD ["gunicorn", "-c", "gunicorn_config.py", "wsgi:app"]
