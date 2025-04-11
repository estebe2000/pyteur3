"""
Configuration Gunicorn pour l'application Pyteur
"""

# Liaison d'adresse IP et port
bind = "0.0.0.0:5001"

# Nombre de processus de travail
workers = 4  # Généralement (2 x nombre de cœurs) + 1

# Nombre de threads par processus de travail
threads = 2

# Timeout en secondes
timeout = 120

# Activer le rechargement automatique en cas de modification du code
reload = False  # Désactivé en production

# Classe de travail
worker_class = "sync"  # Worker class par défaut, plus stable

# Niveau de journalisation
loglevel = "info"

# Fichier de journalisation
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"

# Activer la journalisation des statistiques
statsd_enable = False

# Configuration des en-têtes de sécurité
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Précharger l'application pour améliorer les performances de démarrage
preload_app = True

# Limite de connexions simultanées
worker_connections = 1000

# Limite de requêtes par travailleur avant redémarrage
max_requests = 1000
max_requests_jitter = 50  # Ajoute une variation aléatoire pour éviter le redémarrage simultané

# Hooks de démarrage et d'arrêt
def on_starting(server):
    """
    Exécuté lorsque le serveur démarre.
    """
    print("Démarrage du serveur Gunicorn...")

def on_exit(server):
    """
    Exécuté lorsque le serveur s'arrête.
    """
    print("Arrêt du serveur Gunicorn...")
