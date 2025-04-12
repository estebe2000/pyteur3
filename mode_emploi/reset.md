# 🔄 Réinitialisation de la base de données

![Reset Illustration](https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=800&q=80)

La réinitialisation permet de remettre **Pyteur OS** à zéro : toutes les données (utilisateurs, exercices, documents, etc.) sont supprimées et les comptes par défaut sont recréés.

---

## ⚠️ Attention

> **Cette opération est irréversible !**  
> Toutes les données seront perdues. Pensez à effectuer une sauvegarde avant de réinitialiser la base.

---

## 🖥️ Procédure

- **Sous Windows :**
  ```bat
  reset.bat
  ```
- **Sous Linux/Mac :**
  ```sh
  ./reset.sh
  ```

Cela exécute en interne :
```bash
python manage.py --reset --init
```

---

## 💾 Sauvegarde recommandée

Avant toute réinitialisation, copiez le fichier de base de données (ex : `app/app.db` ou volume Docker) dans un dossier de sauvegarde.

---

## 🔄 Après la réinitialisation

- Les comptes par défaut sont recréés ([voir la liste](comptes)).
- Vous pouvez réimporter des utilisateurs ou des documents si besoin.
- Reconfigurez les paramètres personnalisés (menu, IA, etc.).

---
