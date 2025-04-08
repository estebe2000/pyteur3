import os
import json
import requests
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = "app/ia_providers.json"

class BaseProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt, max_tokens=512, temperature=0.7):
        pass

    @abstractmethod
    def stream_generate_text(self, prompt, max_tokens=512, temperature=0.7):
        pass


class MistralProvider(BaseProvider):
    def __init__(self, api_key, url, model, system_message="Vous êtes un assistant IA utile."):
        self.api_key = api_key
        self.url = url
        self.model = model
        self.system_message = system_message

    def generate_text(self, prompt, max_tokens=512, temperature=0.7):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"Erreur API: {response.status_code}\n{response.text}"
        except Exception as e:
            return f"Erreur: {str(e)}"

    def stream_generate_text(self, prompt, max_tokens=512, temperature=0.7):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        try:
            with requests.post(self.url, headers=headers, json=payload, stream=True, timeout=60) as response:
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


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key, url, model, system_message="You are a helpful assistant."):
        self.api_key = api_key
        self.url = url
        self.model = model
        self.system_message = system_message

    def generate_text(self, prompt, max_tokens=512, temperature=0.7):
        # Implémentation à compléter
        return "OpenAIProvider non implémenté"

    def stream_generate_text(self, prompt, max_tokens=512, temperature=0.7):
        yield "OpenAIProvider streaming non implémenté"


class ProviderManager:
    def __init__(self):
        self.providers = {}
        self.active_provider_name = None
        self.active_provider = None
        self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self.create_default_config()
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.providers = {}
        for name, params in config.get("providers", {}).items():
            provider_type = params.get("type")
            if provider_type == "mistral":
                provider = MistralProvider(
                    api_key=params.get("api_key"),
                    url=params.get("url"),
                    model=params.get("model"),
                    system_message=params.get("system_message", "Vous êtes un assistant IA utile.")
                )
            elif provider_type == "openai":
                provider = OpenAIProvider(
                    api_key=params.get("api_key"),
                    url=params.get("url"),
                    model=params.get("model"),
                    system_message=params.get("system_message", "You are a helpful assistant.")
                )
            else:
                continue
            self.providers[name] = provider
        self.active_provider_name = config.get("active_provider")
        self.active_provider = self.providers.get(self.active_provider_name)

    def create_default_config(self):
        default = {
            "active_provider": "mistral_default",
            "providers": {
                "mistral_default": {
                    "type": "mistral",
                    "api_key": os.getenv("MISTRAL_API_KEY", ""),
                    "url": "https://codestral.mistral.ai/v1/chat/completions",
                    "model": "codestral-latest",
                    "system_message": "Vous êtes un assistant IA utile."
                },
                "openai_default": {
                    "type": "openai",
                    "api_key": "",
                    "url": "https://api.openai.com/v1/chat/completions",
                    "model": "gpt-3.5-turbo",
                    "system_message": "You are a helpful assistant."
                }
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)

    def set_active_provider(self, name):
        if name in self.providers:
            self.active_provider_name = name
            self.active_provider = self.providers[name]
            with open(CONFIG_FILE, "r+", encoding="utf-8") as f:
                config = json.load(f)
                config["active_provider"] = name
                f.seek(0)
                json.dump(config, f, indent=4)
                f.truncate()

    def generate_text(self, prompt, max_tokens=512, temperature=0.7):
        if not self.active_provider:
            return "Aucun fournisseur IA actif"
        return self.active_provider.generate_text(prompt, max_tokens, temperature)

    def stream_generate_text(self, prompt, max_tokens=512, temperature=0.7):
        if not self.active_provider:
            yield "Aucun fournisseur IA actif"
            return
        yield from self.active_provider.stream_generate_text(prompt, max_tokens, temperature)


# Singleton global
provider_manager = ProviderManager()
