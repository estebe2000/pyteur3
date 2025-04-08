#!/bin/bash

echo "Réinitialisation complète de la base de données..."
python3 manage.py --reset --init
echo "Base de données réinitialisée avec succès."
