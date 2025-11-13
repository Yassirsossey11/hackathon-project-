"""
Router pour la gestion des alertes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Alert, Mention
from schemas import AlertResponse
from services.solution_generator import SolutionGenerator

router = APIRouter()

@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer les alertes avec filtres optionnels"""
    query = db.query(Alert)
    
    if resolved is not None:
        query = query.filter(Alert.is_resolved == resolved)
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Récupérer une alerte par ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.get("/{alert_id}/solution")
async def get_alert_solution(alert_id: int, db: Session = Depends(get_db)):
    """Obtenir la solution recommandée pour une alerte"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    mention = db.query(Mention).filter(Mention.id == alert.mention_id).first()
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
    
    solution = SolutionGenerator.generate_solution(mention)
    return {
        "alert_id": alert_id,
        "solution": solution
    }

@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Marquer une alerte comme résolue avec la solution appliquée"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Générer la solution avant de résoudre
    mention = db.query(Mention).filter(Mention.id == alert.mention_id).first()
    solution = None
    if mention:
        solution = SolutionGenerator.generate_solution(mention)
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    
    return {
        "alert": alert,
        "solution_applied": solution
    }

@router.get("/active/count")
async def get_active_alerts_count(db: Session = Depends(get_db)):
    """Obtenir le nombre d'alertes actives"""
    count = db.query(Alert).filter(Alert.is_resolved == False).count()
    return {"active_alerts": count}

