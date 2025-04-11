@echo off
REM Script pour démarrer automatiquement les conteneurs Docker au démarrage de Windows
REM À placer dans le dossier de démarrage: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

cd /d C:\Users\estebe2000\Documents\GitHub\pyteur3
docker-compose -f docker-compose-gunicorn.yml up -d
