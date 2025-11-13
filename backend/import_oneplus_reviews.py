"""
Script pour importer les avis OnePlus Nord CE 2 dans la base de données.
"""
import csv
import io
from datetime import datetime, timedelta
import random

from database import engine, Base, SessionLocal
from models import Entity, Mention, SentimentType, SourceType, Alert
from services.reason_classifier import determine_reason
from services.sentiment_analyzer import SentimentAnalyzer


RAW_CSV = """Review-Title,rating,Review-Body,Product Name
Worst phone ever,1.0 out of 5 stars,Hang problem,"OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Ok !!! Not up to the mark,2.0 out of 5 stars,"I'm writing this review after using 3days !!! Be to honest this is normal Android phone It's not like OnePlus Camera quality very low it says 64mp but not Sound also low Battery backup ok !!! For one day normal use its If ur Gamer don't go for it Overall price it High for this handset If u really wanna buy OnePlus ho for higher end model I'm first time buying OnePlus Little disappointment","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Awesome look,5.0 out of 5 stars,"Camera is so good n very fast phone back look is awesome. With this price segment it's worth it and the most important thing is the phone has dedicated memory card slot. Battery backup is also good and with the help of 65w charger you can charge your phone from 50-100% in just 15 mins. Super vooc charger charges very fast. Very smooth touch and very fast phone, you can play games with no lag.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
One plus losing is originality!!!,3.0 out of 5 stars,"It's an average product, decent for day to day activity. Camera is average, performance is fine. OnePlus is losing it's originality, Warp charger to VOOC charger! I wish OnePlus keeps its originality. Thanks Amazon for the hassle free exchange.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Read,1.0 out of 5 stars,"Phone delivered with damaged display. Replacement took time but finally received perfect phone. Camera quality is as expected, overall performance best. You can go for it.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Fantastic but some bug fixes required!,4.0 out of 5 stars,"Phone is fab! But some apps like Gaana, LinkedIn etc are crashing. Need bug fixes. Camera good, finish good, sound could be better. Touch awesome, fingerprint fast, face unlock excellent. Charging speed super quick (~40 min).","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
A good choice for upgrade,5.0 out of 5 stars,"Decent battery life and excellent charging speed. Smooth performance and display. Compact and lightweight. Design neat. Cons: Speaker isn't great, camera okayish. Overall a good phone with headphone jack and expandable memory.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Camera is not good... oppo is the best,3.0 out of 5 stars,"Phone overall good but some heating problem and selfie camera is not too good. Otherwise phone is good.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
"VERY DISAPPOINTED BY 1PLUS. Sound and back camera poor quality.",1.0 out of 5 stars,"For 25k poor build quality. Audio is worst, single speaker low volume. Back camera not good. Touch feels laggy. Fast charging and battery backup good. Overall not worth the price.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Excellent all rounder!,5.0 out of 5 stars,"Grey mirror finish is really cool and the phone is smooth in day to day usage. Charging speed is very fast. Cameras are all good and on par with competition. A very good phone in this price range.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
bakwas mobile hai,1.0 out of 5 stars,Bakwas mobile hai,"OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
amazing,5.0 out of 5 stars,"Very amazingly built and decently featured smartphone. Battery lasts full day, charges really fast. Smooth fingerprint scanner. Camera decent as per price.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
"A decent package for non gamers",4.0 out of 5 stars,"Lightweight phone comfortable for one hand usage. AMOLED 90Hz screen good. Performance solid for daily tasks; heating manageable. Cameras decent but not the best. Battery lasts more than 1.5 days with 65W fast charge.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Phone hang issue,3.0 out of 5 stars,"Phone is good but hangs every hour, SAR value high. Needs improvement.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Good overall performance,4.0 out of 5 stars,"Lightweight and slim. Good look and specs. Refresh rate amazing given cost. Satisfied so far.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Amazing Phone,5.0 out of 5 stars,"Best OS after iPhone. Camera good enough. AMOLED display amazing. Loud sound. No heating issue. Charges very fast. Worth the cost.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Better than Realme 9 Pro+,5.0 out of 5 stars,"Major weak points: no stereo speakers, no RAM expansion, struggles in low-light. Should improve camera via update. Otherwise great value.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Mid ranger Flagship.,5.0 out of 5 stars,"Great deal. Design premium, packaging impressive. 65W charger included. Supports multiple 5G bands, dual SIM, expandable memory. Software smooth, battery fast charge. Camera good but low light could be better.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Hang problem,2.0 out of 5 stars,"Worked well for 2 days then continuous hang problem, need restart twice a day. Processor cannot handle load.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Disappoint with build quality and display,1.0 out of 5 stars,"Display and camera not up to mark. Feels lower segment despite price.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Don't buy,1.0 out of 5 stars,"Refresh rate drops during gaming. Processor and display refresh not good. Exchange policy cuts bonus amount.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
3rd class camera don't buy this phone,1.0 out of 5 stars,"Camera is very poor. Don't buy this product.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Read this before you buy this!!!!,4.0 out of 5 stars,"UI extremely clean. Battery charges in 30-35 minutes. PUBG runs 56-60 fps. Display jitters in Chrome unless high performance mode enabled.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Worst phone ever. Lagging since first day.,1.0 out of 5 stars,"Poor camera, lagging throughout. Worst phone ever.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
"Bad camera, slow processor. Not value for money.",1.0 out of 5 stars,"Pros: good battery, fast charging, slim. Cons: slow processor, low camera quality, not value for money.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
"Not worthable, many drawbacks",2.0 out of 5 stars,"Overheating while charging and browsing, fast battery drain, face unlock unreliable, phone hangs, Bluetooth call volume low. Not worth the price.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Worst phone ever,1.0 out of 5 stars,"Worst phone of my life.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Super,5.0 out of 5 stars,"Great phone, very satisfied.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Average Phone. Keep average expectations.,3.0 out of 5 stars,"Design good, comfortable. Performance good but phone heats on continuous usage. Battery okayish, charges 0-80 in 25 minutes. Camera decent but not OnePlus flagship level.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Value for money,5.0 out of 5 stars,"Design awesome, fast charger, more 5G bands, camera setup great.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Sleek and sharp,5.0 out of 5 stars,"Beautiful phone.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Awesome mobile Just go for it,5.0 out of 5 stars,"Fluid AMOLED screen, 64MP camera, 65W charging, Oxygen OS. Overall feature-rich and affordable.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Nice phone,5.0 out of 5 stars,"Very good product.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Not expected this from a OnePlus phone,2.0 out of 5 stars,"Fingerprint scan not smooth. Camera poor in low light. Missing stock OnePlus apps. Call recorder announcement annoying. Heating on hotspot use. Battery drains fast. No Android 12 yet. No stereo speaker.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
One plus did it again!,5.0 out of 5 stars,"Good value phone to gift. Feels amazing to use. Highly recommended in this price range.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
One of the best midrange 5G Phone,4.0 out of 5 stars,"Superb display, cool design, light weight. Fast charging. Go for it.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Hands-off performance... Thanks 1+,5.0 out of 5 stars,"Great fast charging and expandable storage. Camera okay for the price. Overall good.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Good phone,5.0 out of 5 stars,"Beautiful, smooth, fast charging. Processor good, gaming very good, outdoor photos nice. Cons: Android 11, no stereo speaker.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Confusing SIM card slot,1.0 out of 5 stars,"Sim/MicroSD slot confusing to operate. Poor first-time experience.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
"Not for any audiophile, USB audio is buggy",2.0 out of 5 stars,"USB audio merged with OTG causing issues with external DACs. Need to restart devices. Not suitable for audiophiles.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Very light in weight with beast performance.,4.0 out of 5 stars,"Design and back panel shiny finish great. Happy with fast charging. Camera alignment awesome.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Looks good so far,5.0 out of 5 stars,"Using since 2 days. No hanging issue, works smooth. Camera good, macro average. No bloatware. Case provided is poor quality.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
It's the Worst OnePlus phone Ever,1.0 out of 5 stars,"Lag in audio while shooting video, hangs often, microphone worst, face unlock unreliable. Not up to OnePlus standards.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Very good phone,5.0 out of 5 stars,"All good but heating problem only.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Camera,5.0 out of 5 stars,"All good but camera not improved.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
OnePlus Nord CE 2- Excellent Quality,4.0 out of 5 stars,"Sim and memory card slot useful. On-screen fingerprint scanner. Camera quality good, fast charging 30 mins. 90Hz refresh rate. Gray mirror colour not great. Alert slider missing.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Great Cell,5.0 out of 5 stars,"Charging speed surprising. Battery optimization great. Missing stock OnePlus phone app. Overall happy.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
It's really a bomb,1.0 out of 5 stars,"Gets heated while receiving notifications and charging. Screen mark appeared. Feels fooled.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Simply Amazing,4.0 out of 5 stars,"Oxygen OS smooth, loud speaker, headphone jack output crisp. Camera needs optimization in low light. Light weight device, good brand value.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
"Obviously a good product, original",5.0 out of 5 stars,"Best mid range product, good camera, good display, smooth usage.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Value for money,5.0 out of 5 stars,"Great phone, like it.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Just awesome experience,5.0 out of 5 stars,"Phone looks amazing and performance too. Display awesome, camera up to mark. If you get around 16k go for it.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Good phone,5.0 out of 5 stars,"Best looking phone for the price. Extend RAM up to 3GB. Pros: looks, fast charging, great video stabilisation, HDR display, Oxygen OS. Cons: 90Hz only, speakers not loud, no wireless charging, low light photography poor.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Great value phone for the price!,5.0 out of 5 stars,"Switched from Samsung M51. Smooth, bright display. No bloatware. Camera fine for needs. Charges fast, comfortable size, no overheating.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Worst phone,1.0 out of 5 stars,"Not up to the mark.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Fantastic!!! Worth every penny,5.0 out of 5 stars,"Superb smartphone. Great looks, build, performance, OS. Only dislike is Google phone app call recording warning.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Average phone,3.0 out of 5 stars,"True OnePlus fan disappointed. Great feel, battery, charging. Not a gaming phone, camera not good, body plastic, speaker placement poor.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
after using 1 week,5.0 out of 5 stars,"Awesome, only wants latest Android.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Worst phone ever.,1.0 out of 5 stars,"Phone hangs, call sound poor, extremely slow, camera pixelated. Regret buying.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
It's a better smartphone but not very good.,3.0 out of 5 stars,"Fingerprint quick, battery life good, camera decent, MediaTek processor. Display 90Hz good but competition offers 120Hz. Good overall but better options exist.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Budget friendly Oneplus Series,4.0 out of 5 stars,"Camera not up to mark but design awesome. Charging super fast but battery backup low.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Absolutely Fantastic Phone,5.0 out of 5 stars,"Best OS after iPhone, camera sharp, AMOLED display amazing, sound loud, no heating, charges to 40% in 15 minutes. 2 year warranty. Great buy.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Not user-friendly mobile,1.0 out of 5 stars,"Many options missing or hard to use. Camera good. Phone started hanging in 2 days. Battery charges fast. For 25k too costly.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Superb charging very good phone,5.0 out of 5 stars,"Totally satisfied. Fast charging impressive.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Just Go for it,5.0 out of 5 stars,"Looks beautiful in blue. Great performance, slim, good battery, fast charge.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
I No like this phone,3.0 out of 5 stars,"No good battery backup.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Best Smartphone in 25K,5.0 out of 5 stars,"Supports triple card slot, 90Hz AMOLED, in-display fingerprint, great camera with EIS, carrier aggregation, smooth UI, WiFi 6, 65W fast charging. Cons: 2MP macro weak, no stereo speakers, 4500mAh battery only, Android 11, 90Hz (not 120).","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
A Fair Selection For your Light Use under 25k,5.0 out of 5 stars,"Happy with the product. Fast charging, 28 hour battery, on-screen fingerprint, light gaming ok. Camera fine but not great for night shots.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Camera Quality is too poor,1.0 out of 5 stars,"Camera quality too poor, feels like local brand. Total waste.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
ONE PLUS NORD CE2 HAVING A DISPLAY ISSUE,1.0 out of 5 stars,"Facing auto display off and erratic multiple display since 3 days. Takes long to restart. Support ticket opened.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
Ultimate Phone,5.0 out of 5 stars,"After 7 days usage, very happy. No hang, no battery heat. Camera good, light weight. Go for it.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
It's a good value for money device by one plus.,5.0 out of 5 stars,"First OnePlus experience good. Not a gamer. Multimedia and casual photos good. Software experience nice without bloatware. Bahamas blue colour exotic.","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
One Plus is Brand,4.0 out of 5 stars,"Good phone overall (review truncated).","OnePlus Nord CE 2 5G (Gray Mirror, 8GB RAM, 128GB Storage)"
"""


def rating_to_sentiment(rating_value: float) -> SentimentType:
    if rating_value >= 4.0:
        return SentimentType.POSITIVE
    if rating_value >= 2.5:
        return SentimentType.NEUTRAL
    return SentimentType.NEGATIVE


def rating_to_score(rating_value: float) -> float:
    """
    Convertit une note sur 5 en score -1..1.
    """
    normalized = max(1.0, min(5.0, rating_value))
    return (normalized - 3.0) / 2.0


def import_reviews():
    print("Initialisation de la base...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    sentiment_analyzer = SentimentAnalyzer()

    try:
        existing = db.query(Entity).filter(Entity.name == "OnePlus Nord CE 2 5G").first()
        if existing:
            print("Suppression des anciennes données OnePlus...")
            db.query(Mention).filter(Mention.entity_id == existing.id).delete()
            db.query(Alert).filter(Alert.mention_id == None).delete()
            db.delete(existing)
            db.commit()

        print("Création de l'entité OnePlus...")
        entity = Entity(
            name="OnePlus Nord CE 2 5G",
            keywords='["OnePlus", "Nord", "CE2", "smartphone", "Android"]',
            description="Avis clients OnePlus Nord CE 2 (Amazon)",
            is_active=True,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)

        reader = csv.DictReader(io.StringIO(RAW_CSV))
        base_date = datetime.utcnow()
        mention_count = 0
        alert_count = 0

        for index, row in enumerate(reader, start=1):
            rating_str = row.get("rating", "").strip()
            try:
                rating_value = float(rating_str.split()[0])
            except (ValueError, IndexError):
                rating_value = 3.0

            sentiment = rating_to_sentiment(rating_value)
            score = rating_to_score(rating_value)

            content = row.get("Review-Body", "").strip()
            if not content:
                continue

            reason_enum, reason_detail = determine_reason(content)
            published_at = base_date - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))

            mention = Mention(
                entity_id=entity.id,
                content=content,
                source=SourceType.WEB,
                source_url=None,
                author=row.get("Review-Title", "").strip() or None,
                sentiment=sentiment,
                sentiment_score=score,
                reason=reason_enum,
                reason_detail=reason_detail,
                published_at=published_at,
                language="en",
            )
            db.add(mention)
            db.flush()
            mention_count += 1

            if sentiment == SentimentType.NEGATIVE and score < -0.5:
                alert = Alert(
                    mention_id=mention.id,
                    severity="high" if score < -0.7 else "medium",
                    message=f"Alerte avis négatif ({reason_enum.value})",
                )
                db.add(alert)
                alert_count += 1

        db.commit()
        print(f"✓ Import terminé : {mention_count} avis insérés, {alert_count} alertes créées.")

    except Exception as exc:
        db.rollback()
        print(f"Erreur lors de l'import : {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import_reviews()

