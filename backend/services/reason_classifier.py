"""
Classification des raisons des avis
"""
from typing import Optional, Tuple
from models import ReasonType

# Mapping de mots-clés vers des catégories (domaine smartphone / produit tech)
REASON_KEYWORDS = {
    ReasonType.PERFORMANCE: [
        "performance", "lag", "lent", "slow", "bug", "freeze", "hang", "stutter", "fps", "gaming",
        "processor", "cpu", "heat", "heating", "overheat", "temperature", "speed"
    ],
    ReasonType.CAMERA: [
        "camera", "photo", "photos", "picture", "image", "video", "selfie", "portrait", "night mode",
        "megapixel", "mp", "hdr"
    ],
    ReasonType.BATTERY: [
        "battery", "charge", "charging", "autonomie", "backup", "drain", "power", "fast charge", "65w",
        "charger", "recharge"
    ],
    ReasonType.BUILD_QUALITY: [
        "build", "quality", "back panel", "design", "look", "feel", "weight", "material", "glass", "plastic",
        "finish"
    ],
    ReasonType.PRICE: [
        "price", "cost", "expensive", "worth", "value", "money", "budget", "overpriced", "deal", "discount"
    ],
    ReasonType.SOFTWARE: [
        "software", "os", "oxygen", "android", "update", "ui", "interface", "coloros", "buggy", "apps",
        "app", "bloatware", "feature"
    ],
    ReasonType.CONNECTIVITY: [
        "network", "5g", "wifi", "bluetooth", "signal", "connectivity", "hotspot", "sim", "slot", "nfc",
        "audio jack", "speaker", "sound"
    ],
    ReasonType.CUSTOMER_SUPPORT: [
        "service", "support", "customer", "amazon", "delivery agent", "replacement", "warranty",
        "technician", "return", "exchange", "support team"
    ],
    ReasonType.DELIVERY: [
        "delivery", "packaging", "box", "damaged", "replacement", "shipping", "courier"
    ],
    ReasonType.EXPERIENCE: [
        "experience", "overall", "usage", "daily", "everyday", "satisfied", "disappointed", "recommend",
        "value for money"
    ]
}

DEFAULT_REASON_DETAIL = {
    ReasonType.PERFORMANCE: "Performances générales, fluidité et chauffe",
    ReasonType.CAMERA: "Qualité photo/vidéo et capteurs",
    ReasonType.BATTERY: "Autonomie et vitesse de charge",
    ReasonType.BUILD_QUALITY: "Qualité de fabrication et design",
    ReasonType.PRICE: "Prix et rapport qualité/prix",
    ReasonType.SOFTWARE: "Système, mises à jour et applications",
    ReasonType.CONNECTIVITY: "Connectivité réseau, audio et accessoires",
    ReasonType.CUSTOMER_SUPPORT: "Support client et service après-vente",
    ReasonType.DELIVERY: "Livraison, emballage et état à la réception",
    ReasonType.EXPERIENCE: "Expérience d'utilisation globale",
    ReasonType.OTHER: "Autres raisons"
}


def determine_reason(
    content: str,
    provided_reason: Optional[ReasonType] = None,
    provided_detail: Optional[str] = None
) -> Tuple[ReasonType, Optional[str]]:
    """
    Déterminer la raison principale d'un avis.
    Si une raison est fournie, elle est prioritaire.
    """
    if provided_reason:
        detail = provided_detail or DEFAULT_REASON_DETAIL.get(provided_reason, None)
        return provided_reason, detail

    text = content.lower()
    for reason_type, keywords in REASON_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            detail = provided_detail or DEFAULT_REASON_DETAIL.get(reason_type)
            return reason_type, detail

    return ReasonType.OTHER, provided_detail or DEFAULT_REASON_DETAIL[ReasonType.OTHER]


