"""Chargement et accès à la base de données clients.

Le fichier CSV est chargé une seule fois au démarrage (cache en mémoire) pour
des performances optimales. Toute modification du fichier impose un redémarrage.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from datetime import date
from .config import CLIENTS_CSV

# Cache global (fichier chargé une seule fois)
_df = None
_df_loaded_at = None


def _load() -> pd.DataFrame:
    """Charge et cache le CSV si ce n'est pas déjà fait."""
    global _df, _df_loaded_at
    if _df is not None:
        return _df
    path = Path(CLIENTS_CSV)
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier de données introuvable : {path}. "
            "Vérifie le paramètre CLIENTS_CSV dans config.py."
        )
    df = pd.read_csv(path, dtype=str)
    df["Subscription Date"] = pd.to_datetime(df["Subscription Date"], errors="coerce")
    df["Email Domain"] = df["Email"].str.split("@").str[1].fillna("inconnu")
    _df = df
    _df_loaded_at = path.stat().st_mtime
    return df


def get_clients_dataframe() -> pd.DataFrame:
    """Renvoie le DataFrame (toujours identique, mis en cache)."""
    return _load()


def get_last_modified() -> float:
    """Retourne le timestamp de modification du fichier (None si non chargé)."""
    return _df_loaded_at


def reset_cache() -> None:
    """Vide le cache (utile en développement/test)."""
    global _df, _df_loaded_at
    _df = None
    _df_loaded_at = None
