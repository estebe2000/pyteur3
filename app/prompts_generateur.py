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
Rédige un énoncé clair et précis pour un exercice Python destiné à un élève de niveau {niveau}.

Thème : {theme}
Difficulté : {difficulte}/5
Description : {description}
Debutant : {debutant}
{niveau_python}

IMPORTANT :
- Ne fournis que l'énoncé, sans aucun code, squelette, ni test.
- L'énoncé doit être auto-suffisant et compréhensible.
- Formate ta réponse uniquement en Markdown pur.
"""


def prompt_evaluation_code(code, enonce):
    """
    Construit un prompt pour évaluer un code Python soumis.
    """
    return f"""
Voici l'énoncé de l'exercice :
{enonce}

Voici le code soumis :
```python
{code}
```

Évalue ce code par rapport à l'énoncé.
Identifie les erreurs, suggère des améliorations, et donne un retour constructif.
Réponds uniquement avec du texte formaté en HTML pur.
"""
