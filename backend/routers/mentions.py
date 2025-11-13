"""
Router pour la gestion des mentions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import Mention, Entity, ReasonType
from schemas import MentionResponse, MentionCreate
from services.sentiment_analyzer import SentimentAnalyzer
from services.reason_classifier import determine_reason

router = APIRouter()
sentiment_analyzer = SentimentAnalyzer()

@router.get("/", response_model=List[MentionResponse])
async def get_mentions(
    entity_id: Optional[int] = None,
    source: Optional[str] = None,
    sentiment: Optional[str] = None,
    reason: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Récupérer les mentions avec filtres optionnels"""
    query = db.query(Mention)
    
    if entity_id:
        query = query.filter(Mention.entity_id == entity_id)
    if source:
        query = query.filter(Mention.source == source)
    if sentiment:
        query = query.filter(Mention.sentiment == sentiment)
    if reason:
        try:
            reason_enum = ReasonType(reason)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid reason")
        query = query.filter(Mention.reason == reason_enum)
    
    mentions = query.order_by(desc(Mention.published_at)).offset(skip).limit(limit).all()
    return mentions

@router.get("/{mention_id}", response_model=MentionResponse)
async def get_mention(mention_id: int, db: Session = Depends(get_db)):
    """Récupérer une mention par ID"""
    mention = db.query(Mention).filter(Mention.id == mention_id).first()
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
    return mention

@router.post("/", response_model=MentionResponse)
async def create_mention(mention: MentionCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle mention (avec analyse de sentiment automatique)"""
    # Vérifier que l'entité existe
    entity = db.query(Entity).filter(Entity.id == mention.entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Analyser le sentiment
    analysis = sentiment_analyzer.analyze_sentiment(mention.content)
    reason_enum, reason_detail = determine_reason(
        content=mention.content,
        provided_reason=mention.reason,
        provided_detail=mention.reason_detail
    )
    
    db_mention = Mention(
        entity_id=mention.entity_id,
        content=mention.content,
        source=mention.source,
        source_url=mention.source_url,
        author=mention.author,
        sentiment=analysis["sentiment"],
        sentiment_score=analysis["score"],
        reason=reason_enum,
        reason_detail=reason_detail,
        published_at=mention.published_at,
        language="fr"  # Détection automatique possible
    )
    
    db.add(db_mention)
    db.commit()
    db.refresh(db_mention)
    return db_mention

@router.get("/entity/{entity_id}/stats")
async def get_entity_mention_stats(
    entity_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques de mentions pour une entité"""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    since_date = datetime.utcnow() - timedelta(days=days)
    mentions = db.query(Mention).filter(
        Mention.entity_id == entity_id,
        Mention.published_at >= since_date
    ).all()
    
    total = len(mentions)
    positive = sum(1 for m in mentions if m.sentiment.value == "positive")
    neutral = sum(1 for m in mentions if m.sentiment.value == "neutral")
    negative = sum(1 for m in mentions if m.sentiment.value == "negative")
    reason_counts = {}
    for reason_type in ReasonType:
        count = sum(1 for m in mentions if m.reason == reason_type)
        if count:
            reason_counts[reason_type.value] = count
    
    return {
        "entity_id": entity_id,
        "period_days": days,
        "total_mentions": total,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "sentiment_distribution": {
            "positive": round(positive / total * 100, 2) if total > 0 else 0,
            "neutral": round(neutral / total * 100, 2) if total > 0 else 0,
            "negative": round(negative / total * 100, 2) if total > 0 else 0
        },
        "reason_counts": reason_counts
    }

