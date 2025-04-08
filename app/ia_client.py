import json
import os
import requests

def generate_text(prompt, max_tokens=512, temperature=0.7):
    try:
        with open('app/ia_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except:
        return "Erreur : configuration IA non trouvée."

    provider = config.get('active_provider')

    if provider == 'ollama':
        return call_ollama(prompt, config.get('ollama', {}), max_tokens, temperature)
    elif provider == 'mistral':
        return call_mistral(prompt, config.get('mistral', {}), max_tokens, temperature)
    else:
        return "Aucun fournisseur IA actif."

def call_ollama(prompt, params, max_tokens, temperature):
    url = params.get('url', 'http://localhost:11434')
    model = params.get('model', 'llama2')
    endpoint = url.rstrip('/') + '/api/generate'
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'Réponse vide.')
        else:
            return f"Erreur Ollama: {response.status_code} {response.text}"
    except Exception as e:
        return f"Erreur Ollama: {str(e)}"

def call_mistral(prompt, params, max_tokens, temperature):
    api_key = params.get('api_key')
    url = params.get('url')
    if not api_key or not url:
        return "Clé API ou URL Mistral manquante."
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "codestral-latest",
        "messages": [
            {"role": "system", "content": "Vous êtes un assistant IA utile."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Erreur Mistral: {response.status_code} {response.text}"
    except Exception as e:
        return f"Erreur Mistral: {str(e)}"
