"""
API principale pour l'analyse automatisée de réputation en ligne
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime, timedelta

from database import engine, Base, get_db
from models import Mention, Entity, Alert
from schemas import (
    MentionCreate, MentionResponse, EntityCreate, EntityResponse,
    AlertResponse, ReputationScore, DashboardStats
)
from services.collector import DataCollector
from services.sentiment_analyzer import SentimentAnalyzer
from services.alert_service import AlertService
from routers import entities, mentions, alerts, dashboard, collection, insights

# Créer les tables au démarrage
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Reputation Analysis API",
    description="API pour l'analyse automatisée de réputation en ligne",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(entities.router, prefix="/api/entities", tags=["entities"])
app.include_router(mentions.router, prefix="/api/mentions", tags=["mentions"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(collection.router, prefix="/api/collection", tags=["collection"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])

@app.get("/")
async def root():
    return {
        "message": "Reputation Analysis API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

