"""
Router pour le tableau de bord
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta
from collections import Counter

from database import get_db
from models import Entity, Mention, Alert, ReasonType
from schemas import DashboardStats, ReputationScore, MentionResponse

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Obtenir les statistiques globales du tableau de bord"""
    # Statistiques globales
    total_entities = db.query(Entity).filter(Entity.is_active == True).count()
    total_mentions = db.query(Mention).count()
    active_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()
    
    # Calculer les totaux de sentiment pour Overview Metrics
    mentions = db.query(Mention).all()
    positive_reviews = sum(1 for m in mentions if m.sentiment.value == "positive")
    neutral_reviews = sum(1 for m in mentions if m.sentiment.value == "neutral")
    negative_reviews = sum(1 for m in mentions if m.sentiment.value == "negative")
    
    # Score de réputation moyen
    if mentions:
        # Calculer le score moyen (basé sur sentiment_score)
        avg_score = sum(m.sentiment_score for m in mentions) / len(mentions)
        # Convertir de -1 à 1 vers 0 à 100
        average_reputation = ((avg_score + 1) / 2) * 100
    else:
        average_reputation = 50.0

    reason_counter = Counter()
    for mention in mentions:
        if mention.reason:
            reason_counter[mention.reason.value] += 1

    total_reason_mentions = sum(reason_counter.values())
    reason_percentages = {
        reason: round(count / total_reason_mentions * 100, 2)
        for reason, count in reason_counter.items()
        if total_reason_mentions > 0
    }

    reason_insights = {
        "counts": dict(reason_counter),
        "percentages": reason_percentages,
        "top_reasons": [
            {"reason": reason, "count": count, "percentage": reason_percentages.get(reason, 0)}
            for reason, count in reason_counter.most_common(5)
        ]
    }
    
    # Mentions récentes (7 derniers jours)
    since_date = datetime.utcnow() - timedelta(days=7)
    recent_mentions = db.query(Mention).filter(
        Mention.published_at >= since_date
    ).order_by(desc(Mention.published_at)).limit(10).all()
    
    # Top entités par nombre de mentions
    top_entities_query = db.query(
        Entity.id,
        Entity.name,
        func.count(Mention.id).label('mention_count')
    ).join(Mention).group_by(Entity.id, Entity.name).order_by(
        desc('mention_count')
    ).limit(5).all()
    
    top_entities = []
    for entity_id, entity_name, _ in top_entities_query:
        score = calculate_reputation_score(entity_id, db)
        top_entities.append(score)
    
    return DashboardStats(
        total_entities=total_entities,
        total_mentions=total_mentions,
        active_alerts=active_alerts,
        average_reputation=round(average_reputation, 2),
        recent_mentions=recent_mentions,
        top_entities=top_entities,
        reason_insights=reason_insights
    )

@router.get("/reputation-scores", response_model=List[ReputationScore])
async def get_reputation_scores(db: Session = Depends(get_db)):
    """Obtenir les scores de réputation pour toutes les entités actives"""
    entities = db.query(Entity).filter(Entity.is_active == True).all()
    scores = []
    
    for entity in entities:
        score = calculate_reputation_score(entity.id, db)
        scores.append(score)
    
    return scores

@router.get("/reputation-scores/{entity_id}", response_model=ReputationScore)
async def get_entity_reputation_score(entity_id: int, db: Session = Depends(get_db)):
    """Obtenir le score de réputation pour une entité spécifique"""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return calculate_reputation_score(entity_id, db)

@router.get("/aspect-sentiment")
async def get_aspect_sentiment_analysis(db: Session = Depends(get_db)):
    """Obtenir l'analyse de sentiment par aspect (camera, battery, performance, design, price)"""
    from collections import defaultdict
    
    # Mapping des aspects aux ReasonType
    aspect_mapping = {
        "camera": ReasonType.CAMERA,
        "battery": ReasonType.BATTERY,
        "performance": ReasonType.PERFORMANCE,
        "design": ReasonType.BUILD_QUALITY,
        "price": ReasonType.PRICE,
    }
    
    # Récupérer toutes les mentions avec un reason
    mentions = db.query(Mention).filter(Mention.reason.isnot(None)).all()
    
    # Calculer les statistiques par aspect
    aspect_stats = {}
    for aspect_name, reason_type in aspect_mapping.items():
        aspect_mentions = [m for m in mentions if m.reason == reason_type]
        
        total = len(aspect_mentions)
        positive = sum(1 for m in aspect_mentions if m.sentiment.value == "positive")
        neutral = sum(1 for m in aspect_mentions if m.sentiment.value == "neutral")
        negative = sum(1 for m in aspect_mentions if m.sentiment.value == "negative")
        
        if total > 0:
            aspect_stats[aspect_name] = {
                "total_mentions": total,
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
                "positive_percentage": round(positive / total * 100, 1),
                "neutral_percentage": round(neutral / total * 100, 1),
                "negative_percentage": round(negative / total * 100, 1),
            }
        else:
            aspect_stats[aspect_name] = {
                "total_mentions": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "positive_percentage": 0,
                "neutral_percentage": 0,
                "negative_percentage": 0,
            }
    
    return aspect_stats

def calculate_reputation_score(entity_id: int, db: Session) -> ReputationScore:
    """Calculer le score de réputation pour une entité"""
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    mentions = db.query(Mention).filter(Mention.entity_id == entity_id).all()
    
    total = len(mentions)
    positive = sum(1 for m in mentions if m.sentiment.value == "positive")
    neutral = sum(1 for m in mentions if m.sentiment.value == "neutral")
    negative = sum(1 for m in mentions if m.sentiment.value == "negative")
    reason_distribution = {}
    for reason_type in ReasonType:
        count = sum(1 for m in mentions if m.reason == reason_type)
        if count:
            reason_distribution[reason_type.value] = round(count / total * 100, 2) if total > 0 else 0
    
    # Calculer le score de réputation (0-100)
    if total > 0:
        # Score basé sur la proportion de mentions positives
        reputation_score = ((positive * 1.0 + neutral * 0.5) / total) * 100
    else:
        reputation_score = 50.0  # Score neutre par défaut
    
    # Déterminer la tendance (comparaison avec les 30 derniers jours)
    since_date = datetime.utcnow() - timedelta(days=30)
    recent_mentions = [m for m in mentions if m.published_at >= since_date]
    older_mentions = [m for m in mentions if m.published_at < since_date]
    
    if len(recent_mentions) > 0 and len(older_mentions) > 0:
        recent_positive = sum(1 for m in recent_mentions if m.sentiment.value == "positive")
        older_positive = sum(1 for m in older_mentions if m.sentiment.value == "positive")
        recent_ratio = recent_positive / len(recent_mentions)
        older_ratio = older_positive / len(older_mentions)
        
        if recent_ratio > older_ratio + 0.1:
            trend = "improving"
        elif recent_ratio < older_ratio - 0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    return ReputationScore(
        entity_id=entity_id,
        entity_name=entity.name,
        positive_count=positive,
        neutral_count=neutral,
        negative_count=negative,
        total_mentions=total,
        reputation_score=round(reputation_score, 2),
        sentiment_distribution={
            "positive": round(positive / total * 100, 2) if total > 0 else 0,
            "neutral": round(neutral / total * 100, 2) if total > 0 else 0,
            "negative": round(negative / total * 100, 2) if total > 0 else 0
        },
        reason_distribution=reason_distribution,
        trend=trend
    )

