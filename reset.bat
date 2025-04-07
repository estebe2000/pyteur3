@echo off
echo Suppression de la base de données...
if exist instance\db.sqlite del /Q instance\db.sqlite

echo Réinitialisation de la base...
python init_db.py

echo Base de données réinitialisée avec succès.
pause
