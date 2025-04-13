import os
import sys
import subprocess
import shutil
import glob

DB_PATH = "instance/pyteur.db"
UPLOADS_DIRS = [
    "app/static/uploads/documents",
    "app/static/uploads/exercises"
]

def reset_db():
    if os.path.exists(DB_PATH):
        print(f"Suppression de l'ancienne base de données : {DB_PATH}")
        os.remove(DB_PATH)
    else:
        print("Aucune base de données à supprimer.")
    
    # Vider les répertoires d'uploads
    for dir_path in UPLOADS_DIRS:
        if os.path.exists(dir_path):
            print(f"Vidage du répertoire : {dir_path}")
            files = glob.glob(os.path.join(dir_path, "*"))
            for file_path in files:
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Erreur lors de la suppression de {file_path}. Raison: {e}")
        else:
            print(f"Le répertoire {dir_path} n'existe pas.")

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
