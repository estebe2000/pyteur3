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

# Exposer le port Flask
EXPOSE 5000

# Commande de démarrage
CMD ["python", "run.py"]
