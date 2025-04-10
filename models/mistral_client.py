import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("La clé API Mistral n'est pas configurée dans .env")

MISTRAL_URL = "https://codestral.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "codestral-latest"

SYSTEM_MESSAGE = "Vous êtes un assistant IA utile."

DEFAULT_MAX_TOKENS = 512
DEFAULT_TEMPERATURE = 0.7
DEFAULT_RETRY_COUNT = 2
DEFAULT_RETRY_DELAY = 2  # secondes

def generate_text(prompt, max_tokens=DEFAULT_MAX_TOKENS, temperature=DEFAULT_TEMPERATURE,
                  retry_count=DEFAULT_RETRY_COUNT, retry_delay=DEFAULT_RETRY_DELAY):
    attempts = 0
    while attempts <= retry_count:
        try:
            payload = {
                "model": MISTRAL_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}"
            }
            response = requests.post(MISTRAL_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                # Toujours retourner le message d'erreur API pour debug
                return f"Erreur API: {response.status_code}\n{response.text}"
        except Exception as e:
            # Toujours retourner l'exception pour debug
            return f"Erreur: {str(e)}"


def stream_generate_text(prompt, max_tokens=DEFAULT_MAX_TOKENS, temperature=DEFAULT_TEMPERATURE):
    """
    Génère une réponse en streaming depuis l'API Mistral.
    Retourne un générateur qui yield chaque morceau de texte.
    """
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    try:
        with requests.post(MISTRAL_URL, headers=headers, json=payload, stream=True, timeout=60) as response:
            if response.status_code != 200:
                yield f"[ERREUR API {response.status_code}] {response.text}"
                return
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data:'):
                    data_str = line[5:].strip()
                    if data_str == '[DONE]':
                        break
                    try:
                        data_json = json.loads(data_str)
                        delta = data_json['choices'][0]['delta'].get('content', '')
                        if delta:
                            yield delta
                    except Exception as e:
                        yield f"[ERREUR PARSING] {str(e)}"
    except Exception as e:
        yield f"[ERREUR REQUETE] {str(e)}"
