"""Schémas Pydantic pour la validation des entrées/sorties."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ClientOut(BaseModel):
    """Un client au format de réponse."""

    index: int
    customer_id: str
    first_name: str
    last_name: str
    company: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone_1: Optional[str] = None
    phone_2: Optional[str] = None
    email: Optional[str] = None
    subscription_date: Optional[date] = None
    website: Optional[str] = None


class StatsOut(BaseModel):
    """Statistiques globales du jeu de données."""

    total_clients: int
    nb_countries: int
    nb_cities: int
    first_names: int
    last_names: int
    companies: int
    date_min: str
    date_max: str
    period_days: int
    top_countries: list[dict]  # [{"country": "X", "count": 123}, ...]


class TopOut(BaseModel):
    """Résultat d'une requête 'top n'."""

    metric: str
    top: list[dict]


class ClientsOut(BaseModel):
    """Liste de clients avec pagination."""

    clients: list[ClientOut]
    total: int
    page: int
    page_size: int
