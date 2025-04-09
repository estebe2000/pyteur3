"""
Prompts dédiés au générateur d'exercices IA.
"""

def prompt_generation_exercice(niveau, theme, difficulte, description):
    """
    Construit un prompt pour générer un exercice Python.
    """
    return f"""
Génère un exercice Python pour un élève de niveau {niveau}.
Thème : {theme}
Difficulté : {difficulte}/5
Description : {description}

Fournis un énoncé clair, un squelette de code à compléter, et des consignes adaptées.
Réponds uniquement avec du texte formaté en HTML pur.
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
