"""
Prompts dédiés au générateur d'exercices IA.
"""

def prompt_generation_exercice(niveau, theme, difficulte, description, debutant):
    """
    Construit un prompt pour générer uniquement un énoncé d'exercice Python, sans code.
    """
    niveau_python = ""
    if debutant:
        niveau_python = """
IMPORTANT: Cet exercice est destiné à des débutants en Python. 
N'utilise PAS de fonctions, de classes, d'objets ou d'autres concepts avancés dans le squelette de code.
Utilise uniquement des variables, des opérations de base, des conditions (if/else) et des boucles (for/while).
Le code doit être simple et direct, sans abstractions avancées.
"""
    else:
        niveau_python = """
Cet exercice peut utiliser des fonctions, des classes et d'autres concepts avancés de Python si nécessaire.
"""

    return f"""
Tu es un expert en programmation Python et en pédagogie. 
Tu aides à créer des exercices de programmation pour des élèves de lycée et à évaluer leur code.

Rédige un énoncé clair et précis pour un exercice Python destiné à un élève de niveau {niveau}.

Thème : {theme}
Difficulté : {difficulte}/5
Description : {description}
Debutant : {"true" if debutant else "false"}
{niveau_python}

IMPORTANT :
1. Utilise une structure claire avec des titres et sous-titres bien formatés
2. Fournis un squelette de code avec plusieurs zones à compléter (1-3 minimum) marquées par "# À COMPLÉTER" ou "# VOTRE CODE ICI"
3. Ne fournis jamais de squelette de code fonctionnel déjà complet - il doit toujours y avoir plusieurs parties à implémenter
4. Ne fournis aucun tests ou exemples d'utilisations
5. Le squelette de code dois être dans un SEUL bloc de code
6. L'énoncé doit être auto-suffisant et compréhensible.
7. Formate ta réponse uniquement en Markdown pur.

Exemple de squelette de code CORRECT (avec parties à compléter, non fonctionnel, pour les debutants):

def est_palindrome(chaine):
    # À COMPLÉTER: Normaliser la chaîne (ignorer les espaces et la casse)
    # VOTRE CODE ICI
    
    # À COMPLÉTER: Vérifier si la chaîne normalisée est un palindrome
    # VOTRE CODE ICI
    
    # À COMPLÉTER: Retourner le résultat (True ou False)
    pass

Autre exemple de squelette de code CORRECT (avec parties à compléter, non fonctionnel, pour les debutants):

# Calcul de l'aire en fonction de la forme choisie
if forme == "rectangle":
    # À COMPLÉTER: Calculer l'aire du rectangle
    pass
elif forme == "cercle":
    # À COMPLÉTER: Calculer l'aire du cercle
    pass
elif forme == "triangle":
    # À COMPLÉTER: Calculer l'aire du triangle
    pass
else:
    # À COMPLÉTER: Gérer le cas d'une forme non reconnue
    pass

Exemple de squelette de code INCORRECT (car déjà complet et fonctionnel):

def est_palindrome(chaine):
    # À COMPLÉTER: Normaliser la chaîne (ignorer les espaces et la casse)
    chaine_normalisee = chaine.replace(" ", "").lower()

    # À COMPLÉTER: Vérifier si la chaîne normalisée est un palindrome
    if chaine_normalisee == chaine_normalisee[::-1]:
        return True
    else:
        return False

"""


def prompt_evaluation_code(code, enonce):
    """
    Construit un prompt pour évaluer un code Python soumis.
    """
    return f"""
     Évalue le code Python suivant par rapport à l'énoncé donné:

Voici l'énoncé de l'exercice :
{enonce}

Voici le code soumis :
```python
{code}
```

IMPORTANT: Ton évaluation doit être formatée en HTMarkdown pur pour un affichage correct dans un navigateur.
Ton évaluation doit toujours inclure:
    1. Un titre principal avec # Évaluation du code
    2. Une section sur la conformité à l'énoncé avec ## Conformité à l'énoncé
    3. Une section sur les erreurs potentielles avec ## Erreurs potentielles
    4. Une section sur les suggestions d'amélioration avec ## uggestions d'amélioration:
       - Si le code ne fonctionne pas: fournir UNE seule suggestion principale
       - Si le code fonctionne: fournir 3 suggestions maximum
IMPORTANT: La section "Pour aller plus loin" avec ## Pour aller plus loin ne doit être incluse QUE si le code fonctionne correctement et répond à l'énoncé. Si le code contient des erreurs ou ne répond pas à l'énoncé, n'inclus PAS cette section.
    
    Utilise des émojis pour rendre ton évaluation plus visuelle :
    ✅ Texte : pour les points positifs
    ❌ Texte : pour les erreurs ou problèmes
    💡 Texte : pour les suggestions
    🚀 Texte : pour les conseils d’amélioration
    
    TRÈS IMPORTANT:
    - NE DONNE JAMAIS LA SOLUTION COMPLÈTE à l'exercice
    - Fournis uniquement des notions de cours et des pistes de réflexion
    - Si tu dois donner un exemple de code, utilise un exemple différent de l'exercice ou montre seulement une petite partie de la solution
    - Guide l'élève vers la bonne direction sans faire le travail à sa place
    - Sois encourageant et constructif dans tes retours

"""
