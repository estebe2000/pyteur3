# Mode d’emploi – Pyteur OS

## Table des matières

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Comptes par défaut](#comptes-par-défaut)
4. [Réinitialisation de la base](#réinitialisation-de-la-base)
5. [Structure du projet](#structure-du-projet)
6. [Technologies utilisées](#technologies-utilisées)
7. [Présentation détaillée des fonctionnalités](#présentation-détaillée-des-fonctionnalités)
8. [FAQ et bonnes pratiques](#faq-et-bonnes-pratiques)

---

## Introduction

**Pyteur OS** est une plateforme éducative collaborative open-source, conçue pour l’enseignement de l’informatique (NSI/SNT) au lycée. Elle permet de gérer des classes, de créer et distribuer des exercices (QCM, exercices classiques, flash), de suivre les progrès des élèves, d’intégrer l’IA pour la génération de contenu, et de proposer un environnement numérique complet (messagerie, drive, bac à sable Python, etc.).

---

## Installation

### Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Docker et Docker Compose (optionnel)
- Navigateur web moderne (Chrome, Firefox, Edge, Safari)
- 2 Go RAM minimum (4 Go recommandés)
- 1 Go d’espace disque (hors modèles IA)

### Installation locale

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/estebe2000/pyteur3.git
   cd pyteur3
   ```
2. Créer un environnement virtuel :
   ```bash
   python -m venv .venv
   # Sous Windows :
   .venv\Scripts\activate
   # Sous Linux/Mac :
   source .venv/bin/activate
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Initialiser la base de données :
   ```bash
   python manage.py --init
   ```
5. Lancer l’application :
   ```bash
   python run.py
   ```
   Accès : http://localhost:5000

### Installation avec Docker

- Construction manuelle :
  ```bash
  docker build -t pyteur .
  docker run -p 5000:5000 pyteur
  ```
- Avec Docker Compose (développement) :
  ```bash
  docker-compose up
  ```
- Avec Docker Compose + Gunicorn (production) :
  ```bash
  docker-compose -f docker-compose-gunicorn.yml up
  ```
  Accès : http://localhost:5001

### Configuration IA (Ollama)

Si vous utilisez Ollama, configurez l’URL dans l’interface d’administration :
```
http://ollama:11434
```

---

## Comptes par défaut

À l’installation, trois comptes sont créés automatiquement :

| Type de compte | Identifiant | Mot de passe |
|----------------|-------------|--------------|
| Administrateur | admin       | admin        |
| Professeur     | prof        | prof         |
| Élève          | eleve       | eleve        |

- **Administrateur** : gestion complète du système, utilisateurs, paramètres.
- **Professeur** : gestion des classes, exercices, suivi des élèves.
- **Élève** : accès aux exercices, messagerie, outils pédagogiques.

---

## Réinitialisation de la base

Pour réinitialiser complètement la base de données (remise à zéro, suppression des données, réinstallation des comptes par défaut) :

- **Sous Windows** :
  ```bat
  reset.bat
  ```
- **Sous Linux/Mac** :
  ```sh
  ./reset.sh
  ```

Cela exécute : `python manage.py --reset --init`

---

## Structure du projet

```
├── app/                        # Dossier principal de l'application
│   ├── __init__.py             # Configuration Flask
│   ├── routes/                 # Contrôleurs (blueprints)
│   ├── models.py               # Modèles SQLAlchemy
│   ├── ia_client.py            # Client IA
│   ├── static/                 # Ressources statiques (css, js, uploads)
│   ├── templates/              # Templates Jinja2 (pages)
│   └── lang/                   # Internationalisation
├── docker-compose*.yml         # Configurations Docker
├── Dockerfile                  # Instructions de build Docker
├── manage.py                   # Script de gestion
├── requirements.txt            # Dépendances Python
├── run.py                      # Point d'entrée développement
└── wsgi.py                     # Point d'entrée production
```

---

## Technologies utilisées

- **Backend** : Python 3.10+, Flask, SQLAlchemy, Flask-Login, Flask-WTF, Gunicorn
- **Frontend** : Bootstrap, Tailwind CSS, JavaScript/jQuery, Chart.js, DataTables, FontAwesome
- **IA et intégrations** : Ollama, API Mistral, Basthon (Python dans le navigateur)
- **Déploiement** : Docker, Docker Compose, Gunicorn, scripts d’automatisation

---

## Présentation détaillée des fonctionnalités

Chaque section suivante détaille l’utilité, l’accès, l’interface et l’usage pédagogique de chaque page/module de Pyteur OS.

---

### QCM

**But pédagogique :**  
Permet aux enseignants de créer, modifier et gérer des QCM (questionnaires à choix multiples) pour évaluer les élèves, en s’appuyant sur une banque de questions ou en rédigeant des questions personnalisées. Les QCM peuvent être sauvegardés, partagés, et exportés au format compatible Pronote.

**Accès :**  
- Menu principal > QCM (réservé aux enseignants/professeurs)

**Description de l’interface :**
- **Chargement d’un QCM existant :** Sélectionner un QCM sauvegardé pour le modifier ou le réutiliser.
- **Banque de questions :** Accès à des banques de questions thématiques (NSI, SNT, etc.), possibilité d’importer des questions dans le QCM en cours.
- **Création de question personnalisée :** Rédiger l’énoncé, saisir 4 propositions, sélectionner la bonne réponse, puis ajouter la question au QCM.
- **Liste des questions du QCM :** Visualiser, éditer ou supprimer chaque question du QCM en cours de création.
- **Sauvegarde :** Donner un nom au QCM, puis sauvegarder pour une utilisation ultérieure.
- **Export Pronote :** Générer un fichier XML compatible avec l’import de QCM dans Pronote.
- **Gestion des QCM sauvegardés :** Visualiser la liste, copier le code de partage, supprimer un QCM.

**Exemple d’usage pour un enseignant :**
1. Sélectionner une banque de questions NSI, importer des questions pertinentes.
2. Ajouter des questions personnalisées pour adapter le QCM à la progression de la classe.
3. Sauvegarder le QCM sous un nom explicite (ex : « QCM Réseaux 1ère NSI »).
4. Exporter le QCM au format Pronote pour l’intégrer dans l’ENT ou l’imprimer.
5. Réutiliser ou modifier le QCM pour d’autres classes ou années.

---

### Créateur d’exercices

**But pédagogique :**  
Permet aux enseignants de structurer et d’organiser des exercices par niveau scolaire et par thème, en adaptant la progression pédagogique à la classe. Outil idéal pour préparer des séquences différenciées, des parcours personnalisés ou des référentiels d’exercices.

**Accès :**  
- Menu principal > Créateur d’exercices (réservé aux enseignants/professeurs)

**Description de l’interface :**
- **Choix du niveau scolaire :** Sélectionner le niveau (Troisième, Seconde, SNT, Première, Terminale) pour organiser les exercices.
- **Gestion des thèmes :** Ajouter, nommer et organiser des thèmes pour chaque niveau (ex : « Algorithmique », « Réseaux », « Python », etc.).
- **Édition des niveaux d’exercices :** Pour chaque thème, définir plusieurs niveaux d’exercices, rédiger une description, indiquer si le niveau est adapté aux débutants.
- **Sauvegarde :** Enregistrer la structure complète (niveaux, thèmes, descriptions) pour une utilisation ultérieure ou un partage avec d’autres enseignants.

**Exemple d’usage pour un enseignant :**
1. Créer des thèmes correspondant au programme officiel NSI/SNT pour chaque niveau.
2. Définir des niveaux de difficulté et des descriptions pour chaque thème (ex : « Niveau 1 : découverte », « Niveau 5 : approfondissement »).
3. Utiliser cette structure pour générer ou affecter des exercices adaptés à chaque élève ou groupe.

---

### Générateur d’exercice

**But pédagogique :**  
Permet aux enseignants de générer automatiquement des exercices adaptés au niveau, au thème et à la difficulté choisis, grâce à l’intelligence artificielle (Ollama, Mistral). Idéal pour diversifier les supports, différencier les parcours et gagner du temps dans la préparation.

**Accès :**  
- Menu principal > Générateur d’exercice (réservé aux enseignants/professeurs)

**Description de l’interface :**
- **Choix du niveau, du thème et de la difficulté :** Sélectionner les paramètres pour cibler l’exercice à générer.
- **Génération par IA :** Lancer la génération automatique d’un exercice contextualisé (énoncé, consignes, etc.).
- **Affichage du prompt utilisé :** Visualiser le prompt envoyé à l’IA pour comprendre ou ajuster la génération.
- **Affichage du résultat généré :** Consulter l’exercice produit par l’IA.
- **Téléchargement et ouverture :** Télécharger l’exercice au format notebook ou script Python, ou l’ouvrir directement dans Basthon (console ou notebook) pour une utilisation immédiate en classe.

**Exemple d’usage pour un enseignant :**
1. Sélectionner « Seconde », thème « Algorithmique », difficulté 2.
2. Générer un exercice pour un travail dirigé ou un devoir maison.
3. Télécharger le notebook pour le distribuer aux élèves ou l’ouvrir dans Basthon pour une démonstration en direct.

---

### Statistiques

**But pédagogique :**  
Offre aux enseignants et administrateurs un tableau de bord complet pour le suivi de l’activité, des résultats et de l’engagement des élèves. Permet d’identifier les points forts, les difficultés, et d’adapter l’accompagnement pédagogique.

**Accès :**  
- Menu principal > Statistiques (enseignants et administrateurs)

**Description de l’interface :**
- **Utilisateurs :** Statistiques sur les rôles, genres, niveaux, inscriptions. Tableaux et graphiques interactifs, export CSV.
- **Classes & Groupes :** Répartition des élèves par classe/groupe, effectifs, export CSV.
- **Exercices & Documents :** Suivi des créations, affectations, types de documents, export CSV.
- **Messagerie :** Statistiques sur l’utilisation de la messagerie (volume, échanges), export CSV.
- **ToDo Lists :** Suivi des tâches par utilisateur, taux d’achèvement, export CSV.
- **Performances des élèves :** Analyse détaillée des scores aux QCM et devoirs, filtrage par élève, graphiques de progression, export CSV.
- **Interface interactive :** Accordéons pour chaque section, graphiques dynamiques (Chart.js), tableaux filtrables (DataTables).

**Exemple d’usage pour un enseignant :**
1. Analyser la répartition des élèves par niveau et groupe pour adapter les exercices.
2. Suivre la progression d’un élève sur les QCM et devoirs pour proposer un accompagnement personnalisé.
3. Exporter les résultats pour un conseil de classe ou un bilan pédagogique.

---

### Intelligence Artificielle (IA)

**But pédagogique :**  
Met à disposition un assistant conversationnel IA pour les enseignants et les élèves, permettant de générer des contenus, d’obtenir des explications, de corriger des exercices ou de répondre à des questions. Les administrateurs peuvent configurer les fournisseurs IA (Ollama local, Mistral cloud).

**Accès :**  
- Menu principal > Intelligence Artificielle (tous les utilisateurs)
- Configuration avancée réservée aux administrateurs

**Description de l’interface :**
- **Chat IA :** Zone de saisie pour poser des questions, historique des échanges, effacement, copier/coller, support du markdown.
- **Configuration IA (admin) :** Choix du fournisseur (Ollama local, Mistral cloud), configuration de l’URL et de la clé API, sélection et téléchargement des modèles, activation du fournisseur.
- **Utilisation pédagogique :** Génération d’énoncés, correction automatique, aide à la compréhension, différenciation pédagogique.

**Exemple d’usage pour un enseignant :**
1. Demander à l’IA de générer un exercice sur les listes en Python pour la classe de Seconde.
2. Utiliser l’IA pour corriger rapidement une réponse d’élève ou obtenir une explication détaillée.
3. Configurer Ollama localement pour garantir la confidentialité des données élèves.

---

### Gestion des devoirs

**But pédagogique :**  
Permet aux enseignants de créer, d’assigner et de suivre les devoirs pour une classe ou un groupe. Facilite la gestion des échéances, la différenciation et le suivi des rendus.

**Accès :**  
- Menu principal > Gestion des devoirs (enseignants/professeurs)

**Description de l’interface :**
- **Ajout d’un devoir :** Saisie du titre, matière, description, date limite, affectation à une classe ou un groupe.
- **Affectation ciblée :** Choix entre classe entière ou groupe spécifique pour différencier les consignes.
- **Liste des devoirs assignés :** Visualisation de tous les devoirs, avec informations sur la matière, l’échéance, l’affectation, le créateur.
- **Actions :** Modification ou suppression d’un devoir existant.

**Exemple d’usage pour un enseignant :**
1. Créer un devoir de programmation à rendre pour la classe de Première NSI, avec une date limite précise.
2. Affecter un devoir de remédiation à un groupe d’élèves en difficulté.
3. Suivre l’ensemble des devoirs en cours et passés pour préparer les bilans de classe.

---

### Classes & Groupes

**But pédagogique :**  
Permet de structurer l’établissement en classes et groupes, d’organiser les élèves pour la gestion des cours, des devoirs, des exercices différenciés et des suivis personnalisés.

**Accès :**  
- Menu principal > Classes & Groupes (enseignants/professeurs, administrateurs)

**Description de l’interface :**
- **Gestion des classes :** Création, modification, suppression de classes (par niveau et nom).
- **Gestion des groupes :** Création, modification, suppression de groupes au sein d’une classe.
- **Affectation des élèves :** Ajout/retrait d’élèves dans un groupe, visualisation des élèves sans groupe.
- **Navigation :** Sélection d’une classe pour afficher ses groupes, sélection d’un groupe pour gérer ses élèves.

**Exemple d’usage pour un enseignant :**
1. Créer les classes de Seconde, Première, Terminale NSI/SNT en début d’année.
2. Constituer des groupes de besoins ou de projets pour la différenciation pédagogique.
3. Affecter rapidement un élève à un groupe de remédiation ou d’approfondissement.

---

### Utilisateurs

**But pédagogique :**  
Permet de gérer l’ensemble des utilisateurs de la plateforme (administrateurs, professeurs, élèves), d’ajouter ou de modifier des comptes, d’importer des élèves en masse, et d’assurer la sécurité des accès.

**Accès :**  
- Menu principal > Utilisateurs (administrateurs, professeurs selon droits)

**Description de l’interface :**
- **Liste des utilisateurs :** Visualisation séparée des administrateurs, professeurs et élèves.
- **Ajout d’utilisateur :** Formulaire pour créer un nouveau compte (nom, prénom, email, rôle, etc.).
- **Modification/Suppression :** Accès à l’édition ou à la suppression de chaque utilisateur.
- **Importation d’élèves :** Import en masse via un fichier CSV pour faciliter la rentrée ou l’intégration d’une nouvelle classe.

**Exemple d’usage pour un enseignant/administrateur :**
1. Ajouter un nouveau professeur ou élève en cours d’année.
2. Importer toute une classe d’élèves à partir d’un fichier fourni par l’établissement.
3. Modifier les informations d’un utilisateur ou réinitialiser un mot de passe.

---

### Gestion du menu

**But pédagogique :**  
Permet d’adapter l’interface de la plateforme aux besoins de l’établissement ou de la classe, en personnalisant les sections visibles du menu et en ajoutant des liens externes utiles (ENT, outils, ressources pédagogiques…).

**Accès :**  
- Menu principal > Gestion menu (administrateurs)

**Description de l’interface :**
- **Sections internes :** Activer ou désactiver la visibilité de chaque section du menu principal pour tous les utilisateurs.
- **Liens externes :** Ajouter, modifier, supprimer des liens personnalisés (nom, URL, icône, comportement d’ouverture).
- **Personnalisation avancée :** Choix d’icônes, ordre des liens, ouverture dans une fenêtre ou un nouvel onglet.

**Exemple d’usage pour un administrateur :**
1. Masquer temporairement certaines fonctionnalités (ex : Bac à sable) pour une période d’évaluation.
2. Ajouter un lien direct vers l’ENT, Pronote, ou une ressource pédagogique nationale.
3. Adapter le menu à un projet spécifique ou à une expérimentation pédagogique.

---

### Message de bienvenue

**But pédagogique :**  
Permet à l’administrateur ou au professeur de diffuser un message personnalisé à l’ensemble des élèves, visible dès la connexion sur le tableau de bord. Idéal pour transmettre des annonces importantes, des consignes, des encouragements ou des informations institutionnelles.

**Accès :**  
- Menu principal > Édition du message de bienvenue (administrateurs, professeurs selon droits)

**Description de l’interface :**
- **Éditeur de message :** Zone de texte permettant de saisir le message de bienvenue, avec support du HTML basique (gras, italique, listes, liens…).
- **Aperçu et historique :** Visualisation du message actuel et accès à l’historique des messages précédents (date, auteur, contenu).
- **Actions :** Enregistrement du nouveau message, retour au tableau de bord, annulation.

**Exemple d’usage pour un enseignant/administrateur :**
1. Rédiger un message d’accueil pour la rentrée ou une annonce importante (ex : “Bienvenue sur Pyteur OS, pensez à consulter vos devoirs chaque semaine !”).
2. Mettre à jour le message pour annoncer une maintenance, un événement, ou féliciter les élèves.
3. Consulter l’historique pour retrouver d’anciens messages ou suivre la communication institutionnelle.

---

### Tableau de bord

**But pédagogique :**  
Point d’entrée principal de la plateforme, le tableau de bord offre à chaque utilisateur une vue synthétique et personnalisée de son environnement. Il permet d’accéder rapidement aux informations essentielles, aux statistiques globales (pour les administrateurs), et aux actions principales.

**Accès :**  
- Page d’accueil après connexion (tous les utilisateurs)

**Description de l’interface :**
- **Message de bienvenue :** Affiché en haut du tableau de bord, personnalisable par l’administrateur ou le professeur.
- **Statistiques globales (admin) :** Nombre d’élèves, de professeurs, de classes, d’exercices et de documents, sous forme de cartes visuelles.
- **Informations personnelles :** Rôle de l’utilisateur, adresse email, date de dernière connexion.
- **Actions rapides (admin) :** Accès direct à la gestion des utilisateurs, aux statistiques détaillées et aux paramètres.
- **Horloge dynamique :** Affichage de la date et de l’heure en temps réel.

**Exemple d’usage pour un enseignant/administrateur :**
1. Visualiser d’un coup d’œil l’état de la plateforme (effectifs, ressources).
2. Accéder rapidement à la gestion des utilisateurs ou aux statistiques.
3. Lire les annonces importantes via le message de bienvenue.

---

### Applications

**But pédagogique :**  
La section “Applications” regroupe l’ensemble des outils pédagogiques et modules disponibles sur la plateforme Pyteur OS. Elle permet aux utilisateurs d’accéder rapidement à toutes les fonctionnalités essentielles (QCM, exercices, drive, bac à sable, IA, messagerie, etc.) depuis le menu principal. L’administrateur peut personnaliser la visibilité de chaque application selon les besoins de l’établissement ou de la classe.

**Accès :**  
- Menu principal (tous les utilisateurs, selon droits et configuration)

**Description de l’interface :**
- **Liste des applications :** Accès direct à chaque module (tableau de bord, documents, exercices, exercices flash, QCM flash, intelligence artificielle, messagerie, to-do, projets, drive, bac à sable, profil, performance…).
- **Liens externes :** Possibilité d’ajouter des liens personnalisés vers des ressources pédagogiques externes (ex : Py-rates, Scratch).
- **Personnalisation (admin) :** Activation/désactivation de chaque application via la gestion du menu, adaptation de l’interface aux besoins pédagogiques.

**Exemple d’usage pour un enseignant/administrateur :**
1. Accéder rapidement à tous les outils nécessaires pour la gestion de la classe et des activités pédagogiques.
2. Ajouter un lien direct vers une ressource externe utilisée en cours (ex : éditeur Scratch).
3. Adapter le menu pour masquer certaines applications lors d’une période d’évaluation ou d’expérimentation.

---

### Documents

**But pédagogique :**  
Permet de centraliser, partager et organiser les documents pédagogiques (cours, fiches, corrigés, supports PDF…) entre enseignants et élèves. Les documents peuvent être affectés à des classes ou groupes, téléchargés ou consultés en ligne.

**Accès :**  
- Menu principal > Documents (tous les utilisateurs, selon droits)

**Description de l’interface :**
- **Upload de documents :** Ajout de fichiers PDF, possibilité d’ajouter des tags pour faciliter la recherche.
- **Liste des documents :** Tableau listant tous les documents disponibles, avec nom, tags, date d’ajout, actions.
- **Actions disponibles :** Visualiser, télécharger, affecter à une classe/groupe (admin), supprimer (selon droits).
- **Gestion des droits :** Les administrateurs peuvent affecter des documents à des groupes/classes, tous les utilisateurs peuvent télécharger ou consulter les documents qui leur sont accessibles.

**Exemple d’usage pour un enseignant/administrateur :**
1. Déposer un cours ou un corrigé à destination d’une classe ou d’un groupe.
2. Organiser les documents par tags (ex : “NSI”, “SNT”, “Chapitre 1”).
3. Supprimer un document obsolète ou affecter un nouveau document à un groupe spécifique.

---

<!-- Les autres fiches détaillées de chaque fonctionnalité seront ajoutées ici, une par une. -->

---

## FAQ et bonnes pratiques

- Conseils d’utilisation en classe
- Sécurité, sauvegarde, gestion des utilisateurs
- Bonnes pratiques pour la création d’exercices et l’utilisation de l’IA

---

*Document rédigé pour les enseignants de NSI/SNT – Version initiale.*
