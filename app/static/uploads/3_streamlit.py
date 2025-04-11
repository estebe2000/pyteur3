
import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt

def evaluer_mdp(mdp): # Fonction d'évaluation de la force du mot de passe
    score = 0 # Initialisation du score à 0
    caractere = "azertyuiopqsdfghjklmwxcvbn" # Liste des caractères pour vérifier la présence de lettres
    resultats = [] # Liste pour stocker les résultats et messages

    if mdp != mdp.lower():  # Vérification si le mot de passe contient des majuscules
        score += 2 # Ajouter 2 points si le mot de passe contient des majuscules
        resultats.append("Le mot de passe contient des majuscules.")
    
    if mdp != mdp.upper():  # Vérification si le mot de passe contient des minuscules
        score += 1 # Ajouter 1 point si le mot de passe contient des minuscules
        resultats.append("Le mot de passe contient des minuscules.")
    
    if any(caractere.isdigit() for caractere in mdp): # Vérification si le mot de passe contient des chiffres
        score += 2 # Ajouter 2 points si le mot de passe contient des chiffres
        resultats.append("Le mot de passe contient des chiffres.")
    
    if len(mdp) > 12: # Vérification de la longueur du mot de passe
        score += 2 # Ajouter 2 points si le mot de passe contient plus de 12 caractères
        resultats.append("Le mot de passe contient plus de 12 caractères (+2 points).")
    elif 8 <= len(mdp) <= 12:
        score += 2 # Ajouter 2 points si le mot de passe contient entre 8 et 12 caractères
        resultats.append("Le mot de passe contient entre 8 et 12 caractères (+2 points).")

    caracteres_speciaux = "(!@#$%^&*)" # Liste des caractères spéciaux possibles
    if any(caractere in caracteres_speciaux for caractere in mdp): # Vérification si le mot de passe contient des caractères spéciaux
        score += 3 # Ajouter 3 points si le mot de passe contient des caractères spéciaux
        resultats.append("Le mot de passe contient des caractères spéciaux (+3 points).")

    if mdp in mdp_interdits: # Vérification si le mot de passe est trop commun
        score -=5 # Retirer 5 points si le mot de passe est dans la liste des mots de passe interdits
        resultats.append("Le mot de passe est trop commun (-5 points).")
    score = max(0, score)  # Assurer que le score ne soit pas inférieur à 0
    return score, resultats # Retourner le score et les résultats des vérifications

def conseils_personnalises(score): # Fonction pour donner des conseils personnalisés en fonction du score
    if score <= 3:
        return "Votre mot de passe est faible. Essayez d'ajouter des majuscules, des chiffres, et des caractères spéciaux pour le renforcer."
    elif 4 <= score <= 6:
        return "Votre mot de passe est moyen. Vous pouvez l'améliorer en augmentant sa longueur et en évitant les mots communs."
    elif 7 <= score <= 9:
        return "Votre mot de passe est solide. Il est sécurisé, mais vous pouvez encore ajouter des caractères spéciaux pour le renforcer d'avantage."
    else:
        return "Votre mot de passe est très sécurisé. Bravo !"
mdp_interdits = ["1234", "12345", "123456", "1234567", "12345678", "123456789", "password", # Liste des mots de passe interdits trop communs
    "qwerty", "azerty", "admin", "letmein", "welcome", "123123", "111111",
    "monmotdepasse", "abc123", "iloveyou", "password1", "000000", "654321",
    "superman", "batman", "football", "baseball", "master", "sunshine",
    "shadow", "dragon", "trustno1"]

# Titre et sous-titre
st.title("Verificateur et générateur d'un mot de passe avec Streamlit")
st.subheader("Évaluateur de mot de passe")

# Zone de saisie
mdp = st.text_input("Entrez votre mot de passe :",type = "password") 
if st.button("Évaluer"):
        st.success("Merci d'avoir évalué votre mot de passe ! ")
if mdp:
    # Évaluation du mot de passe
    score, resultats = evaluer_mdp(mdp)

    # Affichage des résultats
    st.write(f"**Score :** {score}/10")  # Affichage du score du mot de passe
    st.progress(score * 10) # Affichage d'une barre de progression (en fonction du score)
    conseil = conseils_personnalises(score) # Affichage des conseils personnalisés pour améliorer le mot de passe
    st.write(f"**Conseils pour améliorer votre mot de passe :** {conseil}")
import random
def generer_mot_de_passe(longueur=12, majuscules=True,
minuscules=True, chiffres=True, speciaux=True):

    caracteres = ""
    if majuscules:
        caracteres += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if minuscules:
        caracteres += "abcdefghijklmnopqrstuvwxyz"
    if chiffres:
        caracteres += "0123456789"
    if speciaux:
        caracteres += "!@#$%^&*()-_+=<>?/"
    if not caracteres:
        return "Sélectionnez au moins un type de caractère."
    return "".join(random.choice(caracteres) for _ in range(longueur))
st.subheader("Générateur de mot de passe")

# Sliders et cases à cocher
longueur = st.slider("Choisissez la longueur du mot de passe :", min_value=0, max_value=16, value=12)
inclure_majuscules = st.checkbox("Inclure des majuscules (A-Z)", value=True)
inclure_chiffres = st.checkbox("Inclure des chiffres (0-9)", value=True)
inclure_speciaux = st.checkbox("Inclure des caractères spéciaux (!@#$%^&*...)", value=True)

# Bouton pour générer le mot de passe
if st.button("Générer un mot de passe"):
    mot_de_passe = generer_mot_de_passe(
        longueur= longueur,
        majuscules=inclure_majuscules,
        chiffres=inclure_chiffres,
        speciaux=inclure_speciaux
    )
    st.text_input("Mot de passe généré :", mot_de_passe, type="default")
# Lecture d'un fichier texte
uploaded_file = st.file_uploader("Chargez un fichier texte (.txt)", type="txt")
if uploaded_file:
    contenu = uploaded_file.read().decode("utf-8")
    st.write("Contenu du fichier chargé :")
    st.text(contenu)

# Résultat final
st.write("Merci d'avoir utilisé cette application. 🚀")