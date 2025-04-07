from basthon.autoeval import (
    Validate,
    ValidateVariables,
    ValidateFunction,
    ValidateFunctionPretty,
)
from itertools import product

# cet objet sert à valider le premier point d'arrêt
# sur la cellule d'import mais il ne teste aucun code d'élève
first_cell = Validate()
first_cell()

test_calcul_1 = ValidateVariables({"calcul_1": 1.2 / (2 + 3.5)})
test_calcul_2 = ValidateVariables({"calcul_2": ((1 + 2**2 + 3) / 7) ** 2})

valeurs = range(0, 100)
test_perimetre_carre = ValidateFunction(
    "perimetre_carre", valeurs, target_values=[4 * x for x in valeurs]
)

test_valeur_absolue = ValidateFunctionPretty(
    "valeur_absolue", range(-20, 21), valid_function=abs
)

valeurs = range(-(10**4), 10**4)
test_bissextile = ValidateFunction(
    "bissextile", valeurs, target_values=[a % 4 == 0 and a % 400 != 0 for a in valeurs]
)

test_xor = ValidateFunctionPretty(
    "xor",
    product([True, False], repeat=2),
    valid_function=lambda x, y: x != y,
)
