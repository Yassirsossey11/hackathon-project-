"""
Point d'entrée pour l'API FastAPI sur Vercel
"""
import sys
import os
from pathlib import Path

# Ajouter le dossier backend au path Python
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Importer l'application FastAPI
from main import app
from mangum import Mangum

# Adapter FastAPI pour Vercel avec Mangum
handler = Mangum(app, lifespan="off")

