"""Configuration de l'orchestrateur.

Chaque paramètre expose une variable d'environnement ou une valeur par défaut.
Aucune donnée sensible n'est stockée ici.
"""
from pathlib import Path

# Raccourcis de base de l'application
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "output"

# Chemin vers la base de données clients (CSV nettoyé)
CLIENTS_CSV = DATA_DIR / "customers_clean.csv"

# Alternative (CSV source brut)
# CLIENTS_CSV = Path(r"C:\Users\PC\Desktop\customers.csv.csv")

# Paramètres du serveur
HOST = "0.0.0.0"
PORT = 8000
RELOAD = False  # True en mode développement

# Limite par défaut pour les requêtes de liste
PAGE_SIZE = 100
