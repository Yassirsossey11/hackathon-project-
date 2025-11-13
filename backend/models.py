"""
Modèles de données SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class SourceType(str, enum.Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    WEB = "web"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"

class ReasonType(str, enum.Enum):
    PERFORMANCE = "performance"
    CAMERA = "camera"
    BATTERY = "battery"
    BUILD_QUALITY = "build_quality"
    PRICE = "price"
    SOFTWARE = "software"
    CONNECTIVITY = "connectivity"
    CUSTOMER_SUPPORT = "customer_support"
    DELIVERY = "delivery"
    EXPERIENCE = "experience"
    OTHER = "other"

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    keywords = Column(Text, nullable=False)  # JSON array of keywords
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    mentions = relationship("Mention", back_populates="entity", cascade="all, delete-orphan")

class Mention(Base):
    __tablename__ = "mentions"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(Enum(SourceType), nullable=False)
    source_url = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    sentiment = Column(Enum(SentimentType), nullable=False)
    sentiment_score = Column(Float, nullable=False)  # -1 to 1
    reason = Column(Enum(ReasonType), nullable=True)
    reason_detail = Column(String(255), nullable=True)
    language = Column(String(10), default="fr")
    published_at = Column(DateTime(timezone=True), nullable=False)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    entity = relationship("Entity", back_populates="mentions")
    alerts = relationship("Alert", back_populates="mention", cascade="all, delete-orphan")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    mention_id = Column(Integer, ForeignKey("mentions.id"), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    mention = relationship("Mention", back_populates="alerts")

