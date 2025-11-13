"""
Schémas Pydantic pour la validation des données
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import SentimentType, SourceType, ReasonType

class EntityBase(BaseModel):
    name: str
    keywords: List[str]
    description: Optional[str] = None
    is_active: bool = True

class EntityCreate(EntityBase):
    pass

class EntityResponse(EntityBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MentionBase(BaseModel):
    content: str
    source: SourceType
    source_url: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    reason: Optional[ReasonType] = Field(default=None, description="Catégorie de la raison de l'avis")
    reason_detail: Optional[str] = Field(default=None, description="Description courte de la raison")

class MentionCreate(MentionBase):
    entity_id: int

class MentionResponse(MentionBase):
    id: int
    entity_id: int
    sentiment: SentimentType
    sentiment_score: float
    language: str
    collected_at: datetime
    
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    mention_id: int
    severity: str
    message: str
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ReputationScore(BaseModel):
    entity_id: int
    entity_name: str
    positive_count: int
    neutral_count: int
    negative_count: int
    total_mentions: int
    reputation_score: float  # 0-100
    sentiment_distribution: dict
    reason_distribution: dict
    trend: str  # improving, stable, declining

class DashboardStats(BaseModel):
    total_entities: int
    total_mentions: int
    active_alerts: int
    average_reputation: float
    recent_mentions: List[MentionResponse]
    top_entities: List[ReputationScore]
    reason_insights: dict

class CollectionRequest(BaseModel):
    entity_id: Optional[int] = None
    force: bool = False

