"""
Router pour la gestion des entités (entreprises à surveiller)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from database import get_db
from models import Entity
from schemas import EntityCreate, EntityResponse

router = APIRouter()

@router.post("/", response_model=EntityResponse)
async def create_entity(entity: EntityCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle entité à surveiller"""
    # Vérifier si l'entité existe déjà
    existing = db.query(Entity).filter(Entity.name == entity.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Entity already exists")
    
    db_entity = Entity(
        name=entity.name,
        keywords=json.dumps(entity.keywords),
        description=entity.description,
        is_active=entity.is_active
    )
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    
    # Convertir keywords de JSON string à list pour la réponse
    db_entity.keywords = json.loads(db_entity.keywords)
    return db_entity

@router.get("/", response_model=List[EntityResponse])
async def get_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer toutes les entités"""
    entities = db.query(Entity).offset(skip).limit(limit).all()
    for entity in entities:
        entity.keywords = json.loads(entity.keywords)
    return entities

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: int, db: Session = Depends(get_db)):
    """Récupérer une entité par ID"""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    entity.keywords = json.loads(entity.keywords)
    return entity

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int, 
    entity: EntityCreate, 
    db: Session = Depends(get_db)
):
    """Mettre à jour une entité"""
    db_entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    db_entity.name = entity.name
    db_entity.keywords = json.dumps(entity.keywords)
    db_entity.description = entity.description
    db_entity.is_active = entity.is_active
    
    db.commit()
    db.refresh(db_entity)
    db_entity.keywords = json.loads(db_entity.keywords)
    return db_entity

@router.delete("/{entity_id}")
async def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    """Supprimer une entité"""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    db.delete(entity)
    db.commit()
    return {"message": "Entity deleted successfully"}

