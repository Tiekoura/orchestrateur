"""Application FastAPI orchestrant l'accès aux données clients."""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi import Request
from fastapi.responses import HTMLResponse
from pathlib import Path

from .. import config
from ..services.data_service import (
    get_stats,
    get_top,
    get_clients,
    get_monthly_subscriptions,
    get_email_domains_top,
)

app = FastAPI(
    title="Orchestrateur de données clients",
    description=(
        "API d'accès aux données clients. "
        "Métriques, tri, pagination, historique des inscriptions."
    ),
    version="1.0.0",
)

# CORS (utile en développement ou si l'API est appelée depuis un frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_interface_path = Path(__file__).parent / "interface.html"

# Serveur de l'interface interactive (chemin direct)
@app.get("/interface", response_class=HTMLResponse)
async def serve_interface(request: Request):
    html = _interface_path.read_text(encoding="utf-8")
    return HTMLResponse(html)


# ───────────────── Modèle de réponse global ─────────────────
class ApiResponse(BaseModel):
    ok: bool = True
    data: dict


# ───────────────────── Endpoints ────────────────────────────


@app.get("/", tags=["general"])
def root():
    return {
        "service": "orchestrateur-donnees-clients",
        "version": "1.0.0",
        "status": "opérationnel",
        "docs": "/docs",
    }


@app.get("/health", tags=["état"], response_model=ApiResponse)
def health():
    """Vérifie que le service est opérationnel."""
    try:
        get_stats()  # force le chargement de la base
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"base de données inaccessible : {exc}")
    return {"ok": True, "data": {"status": "ok"}}


@app.get("/stats", tags=["statistiques"], response_model=ApiResponse)
def stats():
    """Statistiques globales du jeu de données."""
    return {"ok": True, "data": get_stats().model_dump()}


@app.get("/top", tags=["triage"], response_model=ApiResponse)
def top(
    metric: str = Query(
        "country",
        description="Critère de tri",
        examples=["country", "city", "first_name", "last_name", "company", "email_domain"],
    ),
    n: int = Query(10, ge=1, le=100),
):
    """
    Top-n des clients selon un critère.

    metric: country | city | first_name | last_name | company | email_domain
    """
    try:
        result = get_top(metric=metric, n=n)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "data": result.model_dump()}


@app.get("/clients", tags=["clients"], response_model=ApiResponse)
def list_clients(
    country: str | None = Query(None, description="Filtre pays (ex: France)"),
    city: str | None = Query(None, description="Filtre ville (ex: Paris)"),
    year: int | None = Query(None, ge=2020, le=2022, description="Année d'inscription"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
):
    """
    Page de clients filtrée.

    Exemple:
      /clients?country=France&year=2021&page=2&page_size=50
    """
    if page_size > 500:
        raise HTTPException(status_code=400, detail="page_size max 500.")
    return {"ok": True, "data": get_clients(
        country=country, city=city, year=year,
        page=page, page_size=page_size,
    )}


@app.get("/monthly", tags=["chronologie"], response_model=ApiResponse)
def monthly():
    """Inscriptions par mois (chronologie)."""
    return {"ok": True, "data": {"series": get_monthly_subscriptions()}}


@app.get("/domains", tags=["contact"], response_model=ApiResponse)
def email_domains(n: int = Query(10, ge=1, le=100)):
    """Top des domaines d'email utilisés."""
    return {"ok": True, "data": get_email_domains_top(n=n).model_dump()}


@app.get("/version", tags=["version"], response_model=ApiResponse)
def version():
    return {"ok": True, "data": {"version": "1.0.0"}}


# ───────────────────── Lancement ────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT, reload=config.RELOAD)
