#!/bin/bash

# Script pour démarrer l'application avec Gunicorn

# Vérifier si l'environnement virtuel existe et l'activer si nécessaire
if [ -d "venv" ]; then
    echo "Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Initialiser la base de données si nécessaire
if [ "$1" = "--reset" ]; then
    echo "Réinitialisation de la base de données..."
    python manage.py --reset --init
else
    echo "Initialisation de la base de données..."
    python manage.py --init
fi

# Démarrer Gunicorn avec le fichier de configuration
echo "Démarrage de Gunicorn avec le fichier de configuration..."
gunicorn -c gunicorn_config.py wsgi:app
