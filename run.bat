@echo off
title Orchestrateur de données clients
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python non détecté. Vérifie le chemin d'installation.
    pause
    exit /b 1
)

echo [1/4] Vérification de l'environnement virtuel ...
if not exist .venv\Scripts\python.exe (
    echo   Création de l'environnement virtuel ...
    python -m venv .venv
)
echo   Installation des dépendances ...
.venv\Scripts\pip.exe install --upgrade pip -q
.venv\Scripts\pip.exe install -r requirements.txt -q

echo [2/4] Lancement du serveur (http://localhost:8000) ...
.venv\Scripts\uvicorn.exe orchestrateur.api.main:app --reload --host 0.0.0.0 --port 8000
