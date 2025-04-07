#!/bin/bash

echo "Suppression de la base de données..."
rm -f instance/db.sqlite

echo "Réinitialisation de la base..."
python3 init_db.py

echo "Base de données réinitialisée avec succès."
