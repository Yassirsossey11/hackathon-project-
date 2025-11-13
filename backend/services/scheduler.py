"""
Service de planification pour la collecte automatique de données
"""
import schedule
import time
import logging
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Entity
from services.collector import DataCollector

logger = logging.getLogger(__name__)

class CollectionScheduler:
    def __init__(self):
        self.running = False
    
    def collect_all_entities(self):
        """Collecter les données pour toutes les entités actives"""
        db = SessionLocal()
        try:
            entities = db.query(Entity).filter(Entity.is_active == True).all()
            collector = DataCollector(db)
            
            for entity in entities:
                try:
                    logger.info(f"Collecting data for entity: {entity.name}")
                    collector.collect_for_entity(entity.id, force=False)
                except Exception as e:
                    logger.error(f"Error collecting for entity {entity.id}: {e}")
        finally:
            db.close()
    
    def start(self, interval_hours: int = 6):
        """Démarrer le planificateur"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        # Planifier la collecte toutes les X heures
        schedule.every(interval_hours).hours.do(self.collect_all_entities)
        
        logger.info(f"Scheduler started. Collection every {interval_hours} hours.")
        
        # Exécuter immédiatement une première collecte
        self.collect_all_entities()
        
        # Boucle principale
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    
    def stop(self):
        """Arrêter le planificateur"""
        self.running = False
        schedule.clear()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scheduler = CollectionScheduler()
    try:
        scheduler.start(interval_hours=6)
    except KeyboardInterrupt:
        scheduler.stop()

