@echo off
REM Script pour démarrer l'application avec Gunicorn sous Windows

REM Vérifier si l'environnement virtuel existe et l'activer si nécessaire
if exist "venv" (
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
)

REM Initialiser la base de données si nécessaire
if "%1"=="--reset" (
    echo Réinitialisation de la base de données...
    python manage.py --reset --init
) else (
    echo Initialisation de la base de données...
    python manage.py --init
)

REM Démarrer Gunicorn avec le fichier de configuration
echo Démarrage de Gunicorn avec le fichier de configuration...
gunicorn -c gunicorn_config.py wsgi:app
