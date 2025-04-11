import json
import os
import requests

def generate_text(prompt, max_tokens=512, temperature=0.7):
    """
    Génère du texte à partir d'un prompt en utilisant le fournisseur d'IA configuré.
    
    Args:
        prompt (str): Le texte d'entrée pour l'IA
        max_tokens (int, optional): Nombre maximum de tokens à générer. Par défaut 512.
        temperature (float, optional): Température pour la génération. Par défaut 0.7.
        
    Returns:
        str: Le texte généré par l'IA
    """
    try:
        with open('app/ia_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        return f"Erreur : configuration IA non trouvée. {str(e)}"

    provider = config.get('active_provider')

    if provider == 'ollama':
        return call_ollama(prompt, config.get('ollama', {}), max_tokens, temperature)
    elif provider == 'mistral':
        return call_mistral(prompt, config.get('mistral', {}), max_tokens, temperature)
    else:
        return "Aucun fournisseur IA actif. Veuillez configurer un fournisseur dans les paramètres."

def call_ollama(prompt, params, max_tokens, temperature):
    """
    Appelle l'API Ollama pour générer du texte.
    
    Args:
        prompt (str): Le texte d'entrée pour l'IA
        params (dict): Paramètres de configuration pour Ollama
        max_tokens (int): Nombre maximum de tokens à générer
        temperature (float): Température pour la génération
        
    Returns:
        str: Le texte généré par Ollama
    """
    url = params.get('url', 'http://localhost:11434')
    model = params.get('model', 'llama2')
    endpoint = url.rstrip('/') + '/api/generate'
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'Réponse vide.')
        else:
            return f"Erreur Ollama: {response.status_code}\n{response.text}"
    except Exception as e:
        return f"Erreur Ollama: {str(e)}"

def call_mistral(prompt, params, max_tokens, temperature):
    """
    Appelle l'API Mistral pour générer du texte.
    
    Args:
        prompt (str): Le texte d'entrée pour l'IA
        params (dict): Paramètres de configuration pour Mistral
        max_tokens (int): Nombre maximum de tokens à générer
        temperature (float): Température pour la génération
        
    Returns:
        str: Le texte généré par Mistral
    """
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
            return f"Erreur Mistral: {response.status_code}\n{response.text}"
    except Exception as e:
        return f"Erreur Mistral: {str(e)}"
