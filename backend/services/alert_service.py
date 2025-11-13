"""
Service de gestion des alertes
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from models import Mention, Alert

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_create_alert(self, mention: Mention):
        """Vérifier si une mention nécessite une alerte et la créer si nécessaire"""
        try:
            # Critères pour créer une alerte
            severity = None
            message = ""
            
            # Alerte critique: sentiment très négatif
            if mention.sentiment.value == "negative" and mention.sentiment_score < -0.7:
                severity = "critical"
                message = f"Mention très négative détectée sur {mention.source.value}"
            
            # Alerte haute: sentiment négatif avec score élevé
            elif mention.sentiment.value == "negative" and mention.sentiment_score < -0.5:
                severity = "high"
                message = f"Mention négative détectée sur {mention.source.value}"
            
            # Alerte moyenne: sentiment négatif modéré
            elif mention.sentiment.value == "negative":
                severity = "medium"
                message = f"Mention négative modérée sur {mention.source.value}"
            
            # Vérifier les mots-clés critiques dans le contenu
            critical_keywords = ["scandale", "crise", "problème grave", "erreur critique", 
                               "bug majeur", "défaillance", "incident"]
            content_lower = mention.content.lower()
            
            if any(keyword in content_lower for keyword in critical_keywords):
                if severity != "critical":
                    severity = "high"
                    message = f"Mention contenant des mots-clés critiques sur {mention.source.value}"
            
            # Créer l'alerte si nécessaire
            if severity:
                alert = Alert(
                    mention_id=mention.id,
                    severity=severity,
                    message=message
                )
                self.db.add(alert)
                self.db.commit()
                logger.info(f"Alert created for mention {mention.id}: {severity}")
        
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            self.db.rollback()
    
    def get_active_alerts_count(self) -> int:
        """Obtenir le nombre d'alertes actives"""
        return self.db.query(Alert).filter(Alert.is_resolved == False).count()
    
    def get_critical_alerts(self, limit: int = 10):
        """Obtenir les alertes critiques"""
        return self.db.query(Alert).filter(
            Alert.severity == "critical",
            Alert.is_resolved == False
        ).order_by(Alert.created_at.desc()).limit(limit).all()

