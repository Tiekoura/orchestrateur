# Orchestrateur de données clients (FastAPI)

API d'accès structuré aux données clients côté `customers.csv`. L'API expose
des méta-données, une pagination filtrage, des tops et une chronologie.

## Structure du projet

```
orchestrateur/
├── orchestrateur/          # Package Python
│   ├── __init__.py
│   ├── config.py           # Chemins et paramètres du serveur
│   ├── schemas.py          # Modèles Pydantic (validation)
│   ├── loader.py           # Chargement cache du CSV
│   ├── api/
│   │   └── main.py         # Définition des endpoints
│   └── services/
│       └── data_service.py # Logique métier (stats, tops, clients)
├── .venv/                  # Environnement virtuel (FastAPI, uvicorn...)
├── requirements.txt
└── run.bat                 # Lancement (Windows)
```

## Lancement rapide

1. Activer l'environnement virtuel et installer les dépendances :
   ```bat
   cd C:\Users\PC\Desktop\orchestrateur
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Démarrer le serveur :
   ```bat
   .venv\Scripts\activate
   uvicorn orchestrateur.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Vérifier la santé du service :
   ```
   curl http://localhost:8000/health
   ```

## Endpoints principaux

| Méthode | Chemin          | But                          |
|---------|-----------------|------------------------------|
| GET     | `/`             | Aperçu du service            |
| GET     | `/health`       | Statut du service            |
| GET     | `/stats`        | Statistiques globales        |
| GET     | `/top?metric=x` | Top n (country, city… )      |
| GET     | `/clients`      | Page filtrée (country, city)|
| GET     | `/monthly`      | Inscriptions par mois        |
| GET     | `/domains`      | Top des domaines email       |

Exemple de requête :
```
GET /clients?country=France&year=2021&page_size=50
```

## Remarques

- La base est chargée en mémoire au premier appel (cache).
- Le README, le rapport `.docx` et les graphes se trouvent dans `data/` et `output/` du projet data.
