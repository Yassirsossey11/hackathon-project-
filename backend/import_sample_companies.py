"""
Script pour importer des données d'exemple pour plusieurs entreprises
"""
import json
from datetime import datetime, timedelta
import random

from database import engine, Base, SessionLocal
from models import Entity, Mention, Alert, SentimentType, SourceType, ReasonType
from services.sentiment_analyzer import SentimentAnalyzer
from services.reason_classifier import determine_reason
from services.alert_service import AlertService

# Données d'exemple pour différentes entreprises
SAMPLE_DATA = {
    "Samsung Galaxy S23": {
        "keywords": ["Samsung", "Galaxy S23", "smartphone", "Android"],
        "description": "Samsung Galaxy S23 smartphone reviews",
        "reviews": [
            {
                "content": "Amazing phone! The camera quality is outstanding and battery lasts all day. Very satisfied with my purchase.",
                "rating": 5.0,
                "source": SourceType.WEB,
                "author": "user123"
            },
            {
                "content": "Great display and performance. However, the price is quite high for what you get. Camera could be better in low light.",
                "rating": 4.0,
                "source": SourceType.TWITTER,
                "author": "@techreviewer"
            },
            {
                "content": "Phone keeps overheating during video calls. Battery drains too fast. Not worth the money.",
                "rating": 2.0,
                "source": SourceType.REDDIT,
                "author": "u/dissatisfied_user"
            },
            {
                "content": "Excellent build quality and software experience. One UI is smooth and intuitive.",
                "rating": 5.0,
                "source": SourceType.WEB,
                "author": "samsung_fan"
            },
            {
                "content": "Camera quality is poor compared to competitors. Software updates are slow. Disappointed.",
                "rating": 2.0,
                "source": SourceType.TWITTER,
                "author": "@photographer"
            }
        ]
    },
    "Apple iPhone 14": {
        "keywords": ["Apple", "iPhone 14", "iOS", "smartphone"],
        "description": "Apple iPhone 14 customer reviews",
        "reviews": [
            {
                "content": "Perfect phone! iOS is smooth, camera is incredible, and build quality is premium. Worth every penny.",
                "rating": 5.0,
                "source": SourceType.WEB,
                "author": "apple_lover"
            },
            {
                "content": "Good phone but very expensive. Battery life is decent but could be better. Camera is excellent though.",
                "rating": 4.0,
                "source": SourceType.TWITTER,
                "author": "@techguru"
            },
            {
                "content": "Overpriced for what you get. No significant improvements from previous model. Notch is still annoying.",
                "rating": 3.0,
                "source": SourceType.REDDIT,
                "author": "u/tech_critic"
            },
            {
                "content": "Best smartphone I've ever owned. Everything just works perfectly. Customer service is also excellent.",
                "rating": 5.0,
                "source": SourceType.WEB,
                "author": "happy_customer"
            },
            {
                "content": "Charging port issues after 3 months. Customer support was unhelpful. Very disappointed.",
                "rating": 1.0,
                "source": SourceType.TWITTER,
                "author": "@frustrated_user"
            }
        ]
    },
    "Tesla Model 3": {
        "keywords": ["Tesla", "Model 3", "electric car", "EV"],
        "description": "Tesla Model 3 owner reviews",
        "reviews": [
            {
                "content": "Love my Tesla! Autopilot is amazing, charging is convenient, and the acceleration is incredible.",
                "rating": 5.0,
                "source": SourceType.WEB,
                "author": "tesla_owner"
            },
            {
                "content": "Great car but build quality issues. Panel gaps and paint defects. Service center was helpful though.",
                "rating": 3.5,
                "source": SourceType.TWITTER,
                "author": "@ev_enthusiast"
            },
            {
                "content": "Software updates are fantastic! Car keeps getting better. Range is excellent for daily use.",
                "rating": 5.0,
                "source": SourceType.REDDIT,
                "author": "u/tesla_fan"
            },
            {
                "content": "Autopilot stopped working after update. Service appointment took 2 weeks. Very frustrating experience.",
                "rating": 2.0,
                "source": SourceType.WEB,
                "author": "concerned_owner"
            },
            {
                "content": "Best car I've ever driven. Supercharger network is convenient. No regrets!",
                "rating": 5.0,
                "source": SourceType.TWITTER,
                "author": "@ev_lover"
            }
        ]
    }
}

def import_sample_companies():
    """Importer les données d'exemple"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    sentiment_analyzer = SentimentAnalyzer()
    alert_service = AlertService(db)
    
    try:
        base_date = datetime.utcnow()
        
        for company_name, company_data in SAMPLE_DATA.items():
            # Vérifier si l'entité existe
            entity = db.query(Entity).filter(Entity.name == company_name).first()
            
            if entity:
                print(f"Entity {company_name} already exists. Skipping...")
                continue
            
            # Créer l'entité
            entity = Entity(
                name=company_name,
                keywords=json.dumps(company_data["keywords"]),
                description=company_data["description"],
                is_active=True
            )
            db.add(entity)
            db.commit()
            db.refresh(entity)
            print(f"✓ Created entity: {company_name}")
            
            # Ajouter les mentions
            for review in company_data["reviews"]:
                # Déterminer le sentiment basé sur la note
                rating = review["rating"]
                if rating >= 4.5:
                    sentiment = SentimentType.POSITIVE
                    sentiment_score = 0.7 + (rating - 4.5) * 0.6
                elif rating >= 3.5:
                    sentiment = SentimentType.POSITIVE
                    sentiment_score = 0.3 + (rating - 3.5) * 0.4
                elif rating >= 2.5:
                    sentiment = SentimentType.NEUTRAL
                    sentiment_score = (rating - 2.5) * 0.2
                else:
                    sentiment = SentimentType.NEGATIVE
                    sentiment_score = -0.7 - (2.5 - rating) * 0.3
                
                # Analyser le sentiment avec l'analyseur
                analysis = sentiment_analyzer.analyze_sentiment(review["content"])
                
                # Déterminer la raison
                reason_enum, reason_detail = determine_reason(review["content"])
                
                # Date aléatoire dans les 30 derniers jours
                days_ago = random.randint(0, 30)
                published_at = base_date - timedelta(
                    days=days_ago,
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                mention = Mention(
                    entity_id=entity.id,
                    content=review["content"],
                    source=review["source"],
                    source_url=f"https://example.com/review/{company_name.replace(' ', '_')}/{random.randint(1, 1000)}",
                    author=review["author"],
                    sentiment=analysis["sentiment"],
                    sentiment_score=analysis["score"],
                    reason=reason_enum,
                    reason_detail=reason_detail,
                    published_at=published_at,
                    language="en"
                )
                
                db.add(mention)
                db.flush()
                
                # Créer des alertes si nécessaire
                alert_service.check_and_create_alert(mention)
            
            db.commit()
            print(f"  → Added {len(company_data['reviews'])} reviews for {company_name}")
        
        # Statistiques finales
        total_entities = db.query(Entity).count()
        total_mentions = db.query(Mention).count()
        total_alerts = db.query(Alert).count()
        
        print(f"\n✓ Import completed!")
        print(f"  - Total entities: {total_entities}")
        print(f"  - Total mentions: {total_mentions}")
        print(f"  - Total alerts: {total_alerts}")
        
    except Exception as e:
        db.rollback()
        print(f"Error during import: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import_sample_companies()

