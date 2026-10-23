"""Service métier : requêtes sur la base de clients.

Chaque fonction est une "tâche d'orchestration" : elle lit la base, filtre /
agrège et renvoie un résultat normalisé (dict compatible JSON).
"""

import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime
from ..loader import get_clients_dataframe, get_last_modified, reset_cache
from ..schemas import ClientOut, StatsOut, TopOut


def _to_client_row(row: pd.Series) -> ClientOut:
    """Convertit une ligne DataFrame en ClientOut."""
    return ClientOut(
        index=int(row["Index"]),
        customer_id=str(row["Customer Id"]).strip(),
        first_name=str(row["First Name"]).strip(),
        last_name=str(row["Last Name"]).strip(),
        company=str(row["Company"]).strip() if pd.notna(row["Company"]) else None,
        city=str(row["City"]).strip() if pd.notna(row["City"]) else None,
        country=str(row["Country"]).strip() if pd.notna(row["Country"]) else None,
        phone_1=str(row["Phone 1"]).strip() if pd.notna(row["Phone 1"]) else None,
        phone_2=str(row["Phone 2"]).strip() if pd.notna(row["Phone 2"]) else None,
        email=str(row["Email"]).strip() if pd.notna(row["Email"]) else None,
        subscription_date=row["Subscription Date"].date() if pd.notna(row["Subscription Date"]) else None,
        website=str(row["Website"]).strip() if pd.notna(row["Website"]) else None,
    )


def _to_dict(client: ClientOut) -> dict:
    return client.model_dump()


def get_stats() -> StatsOut:
    """Calcule et retourne les statistiques globales."""
    df = get_clients_dataframe()
    yearly = df.groupby(df["Subscription Date"].dt.year).size()

    top_countries = (
        df["Country"].value_counts().head(8).reset_index(name="count")
    )
    top_countries = top_countries.rename(columns={"Country": "country"})
    top_countries["country"] = top_countries["country"].astype(str)

    date_min = df["Subscription Date"].min().strftime("%d/%m/%Y")
    date_max = df["Subscription Date"].max().strftime("%d/%m/%Y")
    period_days = (df["Subscription Date"].max() - df["Subscription Date"].min()).days

    return StatsOut(
        total_clients=int(len(df)),
        nb_countries=int(df["Country"].nunique()),
        nb_cities=int(df["City"].nunique()),
        first_names=int(df["First Name"].nunique()),
        last_names=int(df["Last Name"].nunique()),
        companies=int(df["Company"].nunique()),
        date_min=date_min,
        date_max=date_max,
        period_days=period_days,
        top_countries=top_countries.to_dict(orient="records"),
    )


def get_top(metric: str, n: int = 10) -> TopOut:
    """
    Retourne les n premiers éléments pour un critère donné.

    metric:
      - country
      - city
      - first_name
      - last_name
      - company
      - email_domain
    """
    valid_metrics = {"country", "city", "first_name", "last_name", "company", "email_domain"}
    if metric not in valid_metrics:
        raise ValueError(
            f"Métrique inconnu. Choix: {sorted(valid_metrics)}."
        )

    df = get_clients_dataframe()
    col_map = {
        "country": "Country",
        "city": "City",
        "first_name": "First Name",
        "last_name": "Last Name",
        "company": "Company",
        "email_domain": "Email Domain",
    }
    col = col_map[metric]

    counts = df[col].fillna("inconnu").value_counts().head(n).reset_index(name="count")
    counts = counts.rename(columns={col: metric})
    counts[metric] = counts[metric].astype(str)

    return TopOut(
        metric=metric,
        top=[{metric: row[metric], "count": int(row["count"])} for row in counts.to_dict(orient="records")],
    )


def get_clients(country: Optional[str] = None, city: Optional[str] = None,
                year: Optional[int] = None, page: int = 1, page_size: int = 100) -> dict:
    """
    Retourne une page de clients filtrée.

    Filtres: country, city, year (année d'inscription).
    Pagination: page (début à 1), page_size.
    """
    df = get_clients_dataframe()

    if country:
        df = df[df["Country"].str.strip().str.lower() == str(country).strip().lower()]
    if city:
        df = df[df["City"].str.strip().str.lower() == str(city).strip().lower()]
    if year:
        df = df[df["Subscription Date"].dt.year == int(year)]

    total = len(df)
    if total == 0:
        return {"clients": [], "total": 0, "page": page, "page_size": page_size}

    start = (page - 1) * page_size
    end = start + page_size
    subset = df.iloc[start:end]

    clients = [_to_dict(_to_client_row(row)) for _, row in subset.iterrows()]
    return {"clients": clients, "total": total, "page": page, "page_size": page_size}


def get_monthly_subscriptions() -> list[dict]:
    """Liste des inscriptions par mois."""
    df = get_clients_dataframe()
    monthly = df.groupby([df["Subscription Date"].dt.to_period("M")]).size()
    return [
        {"month": str(period), "count": int(count)}
        for period, count in monthly.items()
    ]


def get_email_domains_top(n: int = 10) -> TopOut:
    """Top n des domaines d'email."""
    return get_top("email_domain", n)


def get_last_modified() -> Optional[float]:
    """Retourne le timestamp de modification du fichier CSV source."""
    return get_last_modified()
