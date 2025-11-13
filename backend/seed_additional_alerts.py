"""
Seed additional mentions to guarantee medium and critical alerts for demo purposes.
"""
from datetime import datetime, timedelta

from database import Base, engine, SessionLocal
from models import Mention, SentimentType, ReasonType, SourceType, Entity
from services.alert_service import AlertService


SEED_ITEMS = [
    {
        "entity": "OnePlus Nord CE 2 5G",
        "mentions": [
            {
                "content": "Battery drain issue persists even after updates, average phone session loses 30% in 20 minutes.",
                "score": -0.45,
                "reason": ReasonType.BATTERY,
                "detail": "Severe battery drain",
                "source": SourceType.WEB,
            },
            {
                "content": "Overheating so bad the device shuts down, serious thermal management failure.",
                "score": -0.82,
                "reason": ReasonType.PERFORMANCE,
                "detail": "Thermal shutdown reported",
                "source": SourceType.TWITTER,
            },
        ],
    },
    {
        "entity": "Samsung Galaxy S23",
        "mentions": [
            {
                "content": "Camera app crashes frequently after last update, customer support keeps delaying fixes.",
                "score": -0.52,
                "reason": ReasonType.SOFTWARE,
                "detail": "Camera app instability",
                "source": SourceType.REDDIT,
            },
            {
                "content": "Critical screen flicker, display unusable at low brightness and Samsung refuses replacement.",
                "score": -0.78,
                "reason": ReasonType.BUILD_QUALITY,
                "detail": "OLED panel defects reported",
                "source": SourceType.WEB,
            },
        ],
    },
    {
        "entity": "Apple iPhone 14",
        "mentions": [
            {
                "content": "New iOS update broke FaceID in enterprise profiles, team productivity heavily impacted.",
                "score": -0.58,
                "reason": ReasonType.SOFTWARE,
                "detail": "FaceID malfunction post update",
                "source": SourceType.WEB,
            },
            {
                "content": "Charging port melted after overnight charge, extremely dangerous!",
                "score": -0.9,
                "reason": ReasonType.BUILD_QUALITY,
                "detail": "Charging port safety issue",
                "source": SourceType.TWITTER,
            },
        ],
    },
    {
        "entity": "Tesla Model 3",
        "mentions": [
            {
                "content": "Software update 2025.04 makes autopilot disengage randomly, scary on the highway.",
                "score": -0.55,
                "reason": ReasonType.PERFORMANCE,
                "detail": "Autopilot disengagement",
                "source": SourceType.REDDIT,
            },
            {
                "content": "Battery pack swelling caused the chassis to lift, Tesla service still has no parts. Serious hazard.",
                "score": -0.88,
                "reason": ReasonType.BATTERY,
                "detail": "Battery swelling hazard",
                "source": SourceType.WEB,
            },
        ],
    },
]


def seed_alerts():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    alert_service = AlertService(db)

    try:
        for item in SEED_ITEMS:
            entity = db.query(Entity).filter(Entity.name == item["entity"]).first()
            if not entity:
                continue

            for idx, mention_data in enumerate(item["mentions"]):
                # Skip if a similar mention already exists
                existing = (
                    db.query(Mention)
                    .filter(
                        Mention.entity_id == entity.id,
                        Mention.content == mention_data["content"],
                    )
                    .first()
                )
                if existing:
                    continue

                published_at = datetime.utcnow() - timedelta(days=idx + 1)
                mention = Mention(
                    entity_id=entity.id,
                    content=mention_data["content"],
                    source=mention_data["source"],
                    sentiment=SentimentType.NEGATIVE,
                    sentiment_score=mention_data["score"],
                    reason=mention_data["reason"],
                    reason_detail=mention_data["detail"],
                    published_at=published_at,
                    language="en",
                )
                db.add(mention)
                db.flush()

                alert_service.check_and_create_alert(mention)
                print(f"✓ Seeded mention for {item['entity']} ({mention_data['reason'].value})")

        db.commit()
        total_alerts = db.query(Mention).count()
        print("\nSeeding completed. Total mentions:", total_alerts)
    except Exception as exc:
        db.rollback()
        print("Error during seeding:", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_alerts()

