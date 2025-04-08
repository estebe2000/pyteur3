# Utilise une image Python officielle
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Créer le répertoire de travail
WORKDIR /app

# Argument pour installation optionnelle d'Ollama
ARG INSTALL_OLLAMA=false

# Installer les dépendances système (et curl si besoin)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl sudo \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Installer Ollama si demandé
RUN if [ "$INSTALL_OLLAMA" = "true" ]; then \
    echo "Installation d'Ollama..."; \
    curl -fsSL https://ollama.com/install.sh | sh; \
    else \
    echo "Ollama non installé (INSTALL_OLLAMA=$INSTALL_OLLAMA)"; \
    fi

# Copier le reste du code
COPY . .

# Exposer le port Flask
EXPOSE 5000

# Commande de démarrage
CMD ["python", "run.py"]
