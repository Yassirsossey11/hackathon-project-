"""
Router pour déclencher la collecte de données
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Entity
from schemas import CollectionRequest
from services.collector import DataCollector

router = APIRouter()

@router.post("/trigger")
async def trigger_collection(
    request: CollectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Déclencher une collecte de données pour une entité ou toutes les entités"""
    collector = DataCollector(db)
    
    if request.entity_id:
        # Collecter pour une entité spécifique
        entity = db.query(Entity).filter(Entity.id == request.entity_id).first()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        background_tasks.add_task(collector.collect_for_entity, request.entity_id, request.force)
        return {
            "message": f"Collection started for entity {request.entity_id}",
            "entity_id": request.entity_id
        }
    else:
        # Collecter pour toutes les entités actives
        entities = db.query(Entity).filter(Entity.is_active == True).all()
        for entity in entities:
            background_tasks.add_task(collector.collect_for_entity, entity.id, request.force)
        
        return {
            "message": f"Collection started for {len(entities)} entities",
            "entities_count": len(entities)
        }

@router.get("/status")
async def get_collection_status():
    """Obtenir le statut de la collecte (pour implémentation future)"""
    return {
        "status": "idle",
        "last_collection": None,
        "next_scheduled": None
    }

