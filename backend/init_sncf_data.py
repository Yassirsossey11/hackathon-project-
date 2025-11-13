"""
Script pour initialiser la base de données avec des données SNCF
"""
from database import engine, Base, SessionLocal
from models import Entity, Mention, Alert, SentimentType, SourceType, ReasonType
from services.sentiment_analyzer import SentimentAnalyzer
from services.reason_classifier import determine_reason
from datetime import datetime, timedelta
import random

def init_sncf_data():
    """Initialiser la base de données avec des données SNCF"""
    # Créer les tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    sentiment_analyzer = SentimentAnalyzer()
    
    try:
        # Vérifier si l'entité SNCF existe déjà
        sncf = db.query(Entity).filter(Entity.name == "SNCF").first()
        
        if sncf:
            print("L'entité SNCF existe déjà. Suppression des anciennes données...")
            # Supprimer les mentions existantes
            db.query(Mention).filter(Mention.entity_id == sncf.id).delete()
            db.query(Entity).filter(Entity.id == sncf.id).delete()
            db.commit()
        
        # Créer l'entité SNCF
        print("Création de l'entité SNCF...")
        sncf = Entity(
            name="SNCF",
            keywords='["SNCF", "TGV", "TER", "train", "gare", "voyage", "transport ferroviaire", "InOui", "Ouigo"]',
            description="Société Nationale des Chemins de fer Français - Service de transport ferroviaire",
            is_active=True
        )
        db.add(sncf)
        db.commit()
        db.refresh(sncf)
        print(f"✓ Entité SNCF créée (ID: {sncf.id})")
        
        # Liste d'avis réels pour la SNCF avec raisons catégorisées
        avis_sncf = [
            # Avis positifs
            {
                "content": "Excellent service TGV aujourd'hui ! Train à l'heure, confortable et personnel très accueillant. Je recommande vivement.",
                "sentiment": "positive",
                "source": SourceType.TWITTER,
                "author": "@voyageur123",
                "reason": ReasonType.PUNCTUALITY,
                "reason_detail": "Train arrivé à l'heure et service global satisfaisant"
            },
            {
                "content": "SNCF : Voyage très agréable en TGV InOui. Wi-Fi gratuit qui fonctionne bien, sièges confortables. Très satisfait du service.",
                "sentiment": "positive",
                "source": SourceType.TWITTER,
                "author": "@trainlover",
                "reason": ReasonType.COMFORT,
                "reason_detail": "Confort à bord et qualité du Wi-Fi"
            },
            {
                "content": "Bravo à la SNCF pour les nouveaux TGV ! Confort optimal, ponctualité au rendez-vous. Un vrai plaisir de voyager.",
                "sentiment": "positive",
                "source": SourceType.NEWS,
                "author": "Le Figaro",
                "reason": ReasonType.EXPERIENCE,
                "reason_detail": "Expérience globale de voyage très positive"
            },
            {
                "content": "Service Ouigo excellent rapport qualité-prix. Train propre, à l'heure, et prix très compétitifs. Parfait pour les petits budgets !",
                "sentiment": "positive",
                "source": SourceType.REDDIT,
                "author": "u/economy_traveler",
                "reason": ReasonType.PRICING,
                "reason_detail": "Tarifs attractifs pour un service efficace"
            },
            {
                "content": "SNCF : Personnel très professionnel et serviable. Ils m'ont aidé avec mes bagages et répondu à toutes mes questions. Merci !",
                "sentiment": "positive",
                "source": SourceType.TWITTER,
                "author": "@happy_traveler",
                "reason": ReasonType.CUSTOMER_SERVICE,
                "reason_detail": "Qualité du service client et assistance en gare"
            },
            {
                "content": "Voyage TER très agréable ce matin. Train moderne, propre, et ponctuel. La SNCF fait du bon travail sur les lignes régionales.",
                "sentiment": "positive",
                "source": SourceType.TWITTER,
                "author": "@regional_user",
                "reason": ReasonType.CLEANLINESS,
                "reason_detail": "Propreté et confort des trains régionaux"
            },
            
            # Avis neutres
            {
                "content": "Voyage SNCF standard. Train à l'heure, rien de particulier à signaler. Service correct sans plus.",
                "sentiment": "neutral",
                "source": SourceType.TWITTER,
                "author": "@neutral_user",
                "reason": ReasonType.EXPERIENCE,
                "reason_detail": "Expérience de voyage conforme aux attentes"
            },
            {
                "content": "SNCF : Information sur les horaires et tarifs disponibles sur le site. Réservation simple et rapide.",
                "sentiment": "neutral",
                "source": SourceType.WEB,
                "author": "Site web",
                "reason": ReasonType.DIGITAL_EXPERIENCE,
                "reason_detail": "Processus de réservation en ligne"
            },
            {
                "content": "Trajet Paris-Lyon en TGV. Durée normale, confort standard. Service comme d'habitude.",
                "sentiment": "neutral",
                "source": SourceType.REDDIT,
                "author": "u/regular_user",
                "reason": ReasonType.COMFORT,
                "reason_detail": "Confort standard sans éléments marquants"
            },
            
            # Avis négatifs
            {
                "content": "SNCF : Retard de 45 minutes sans explication. Très déçu du service aujourd'hui. Manque d'information aux voyageurs.",
                "sentiment": "negative",
                "source": SourceType.TWITTER,
                "author": "@frustrated_user",
                "reason": ReasonType.PUNCTUALITY,
                "reason_detail": "Retard important et manque d'information"
            },
            {
                "content": "Train SNCF annulé au dernier moment ! Aucune alternative proposée. Service client injoignable. Scandaleux !",
                "sentiment": "negative",
                "source": SourceType.TWITTER,
                "author": "@angry_customer",
                "reason": ReasonType.CUSTOMER_SERVICE,
                "reason_detail": "Annulation et absence de prise en charge"
            },
            {
                "content": "SNCF : Wi-Fi ne fonctionne pas, sièges sales, train bruyant. Qualité en baisse constante. Très décevant.",
                "sentiment": "negative",
                "source": SourceType.REDDIT,
                "author": "u/disappointed",
                "reason": ReasonType.CLEANLINESS,
                "reason_detail": "Propreté et confort dégradés"
            },
            {
                "content": "Retard de 2h30 sur un trajet TGV. Aucune compensation proposée. Service client catastrophique. Je vais porter plainte.",
                "sentiment": "negative",
                "source": SourceType.TWITTER,
                "author": "@very_angry",
                "reason": ReasonType.PUNCTUALITY,
                "reason_detail": "Retard majeur sans compensation"
            },
            {
                "content": "SNCF : Prix exorbitants pour un service médiocre. Train bondé, pas de place assise. Scandale des tarifs !",
                "sentiment": "negative",
                "source": SourceType.NEWS,
                "author": "Le Monde",
                "reason": ReasonType.PRICING,
                "reason_detail": "Tarification jugée trop élevée"
            },
            {
                "content": "Problème grave : train SNCF bloqué 3 heures en pleine campagne. Aucune assistance, pas d'eau, pas d'information. Inacceptable !",
                "sentiment": "negative",
                "source": SourceType.TWITTER,
                "author": "@stranded_passenger",
                "reason": ReasonType.SAFETY,
                "reason_detail": "Gestion de crise et sécurité à bord"
            },
            {
                "content": "SNCF : Surcharge des trains, impossibilité de s'asseoir malgré réservation. Service dégradé, qualité en chute libre.",
                "sentiment": "negative",
                "source": SourceType.REDDIT,
                "author": "u/concerned_traveler",
                "reason": ReasonType.COMFORT,
                "reason_detail": "Surcharge et manque de sièges"
            },
            {
                "content": "Retard répété sur la ligne TER. SNCF ne respecte plus les horaires. Frustration quotidienne des usagers.",
                "sentiment": "negative",
                "source": SourceType.NEWS,
                "author": "France Info",
                "reason": ReasonType.PUNCTUALITY,
                "reason_detail": "Retards récurrents sur lignes régionales"
            },
            {
                "content": "SNCF : Application buggée, impossible de récupérer mon billet. Service client injoignable. Très mauvais service.",
                "sentiment": "negative",
                "source": SourceType.TWITTER,
                "author": "@tech_issues",
                "reason": ReasonType.DIGITAL_EXPERIENCE,
                "reason_detail": "Problèmes techniques de l'application mobile"
            },
            {
                "content": "Train SNCF sale et mal entretenu. Toilettes en panne, poubelles pleines. Manque d'hygiène flagrant.",
                "sentiment": "negative",
                "source": SourceType.REDDIT,
                "author": "u/cleanliness_matters",
                "reason": ReasonType.CLEANLINESS,
                "reason_detail": "Hygiène et entretien insuffisants"
            },
        ]
        
        print(f"\nAjout de {len(avis_sncf)} avis SNCF...")
        
        # Générer des dates sur les 30 derniers jours
        base_date = datetime.utcnow()
        
        for i, avis in enumerate(avis_sncf):
            # Date aléatoire dans les 30 derniers jours
            days_ago = random.randint(0, 30)
            published_at = base_date - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # Analyser le sentiment
            analysis = sentiment_analyzer.analyze_sentiment(avis["content"])
            reason_enum, reason_detail = determine_reason(
                content=avis["content"],
                provided_reason=avis.get("reason"),
                provided_detail=avis.get("reason_detail")
            )
            
            # Créer la mention
            mention = Mention(
                entity_id=sncf.id,
                content=avis["content"],
                source=avis["source"],
                source_url=f"https://example.com/mention/{i+1}",
                author=avis["author"],
                sentiment=analysis["sentiment"],
                sentiment_score=analysis["score"],
                reason=reason_enum,
                reason_detail=reason_detail,
                published_at=published_at,
                language="fr"
            )
            
            db.add(mention)
            db.flush()  # Pour obtenir l'ID de la mention
            
            # Créer des alertes pour les mentions très négatives
            if avis["sentiment"] == "negative" and analysis["score"] < -0.6:
                alert = Alert(
                    mention_id=mention.id,
                    severity="high" if analysis["score"] < -0.7 else "medium",
                    message=f"Mention négative détectée sur {avis['source'].value} ({reason_enum.value})"
                )
                db.add(alert)
        
        db.commit()
        
        # Statistiques
        total = db.query(Mention).filter(Mention.entity_id == sncf.id).count()
        positive = db.query(Mention).filter(Mention.entity_id == sncf.id, Mention.sentiment == SentimentType.POSITIVE).count()
        neutral = db.query(Mention).filter(Mention.entity_id == sncf.id, Mention.sentiment == SentimentType.NEUTRAL).count()
        negative = db.query(Mention).filter(Mention.entity_id == sncf.id, Mention.sentiment == SentimentType.NEGATIVE).count()
        alerts_count = db.query(Alert).count()
        reason_counts = {
            reason.value: db.query(Mention).filter(Mention.entity_id == sncf.id, Mention.reason == reason).count()
            for reason in ReasonType
        }
        reason_counts = {k: v for k, v in reason_counts.items() if v > 0}
        
        print(f"\n✓ Données SNCF initialisées avec succès !")
        print(f"\nStatistiques :")
        print(f"  - Total mentions : {total}")
        print(f"  - Positives : {positive}")
        print(f"  - Neutres : {neutral}")
        print(f"  - Négatives : {negative}")
        print(f"  - Alertes créées : {alerts_count}")
        print("  - Répartition des raisons :")
        for reason, count in reason_counts.items():
            print(f"      * {reason}: {count}")
        print(f"\nBase de données prête ! Vous pouvez maintenant lancer le site.")
        
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de l'initialisation : {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    init_sncf_data()

