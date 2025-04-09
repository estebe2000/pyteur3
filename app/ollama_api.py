import requests

OLLAMA_URL = "http://ollama:11434"  # Nom du service dans Docker ou URL par défaut

def pull_model(model_name: str):
    response = requests.post(
        f"{OLLAMA_URL}/api/pull",
        json={"model": model_name}
    )
    if response.status_code == 200:
        return True
    raise Exception(f"Erreur : {response.text}")
