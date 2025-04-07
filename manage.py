import os
import sys
import subprocess

DB_PATH = "instance/pyteur.db"

def reset_db():
    if os.path.exists(DB_PATH):
        print(f"Suppression de l'ancienne base de données : {DB_PATH}")
        os.remove(DB_PATH)
    else:
        print("Aucune base de données à supprimer.")

def init_db():
    print("Création de la base de données...")
    subprocess.run([sys.executable, "init_db.py"], check=True)
    print("Création des comptes administrateur...")
    subprocess.run([sys.executable, "init_admin.py"], check=True)

def main():
    args = sys.argv[1:]
    if "--reset" in args:
        reset_db()
    if "--init" in args:
        init_db()
    if not args:
        print("Utilisation : python manage.py [--reset] [--init]")

if __name__ == "__main__":
    main()
