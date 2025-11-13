"""
Synthetic AI insight generator used to showcase how automated recommendations
could look without calling an external LLM.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from models import Mention, SentimentType, ReasonType


def _format_reason(reason: ReasonType | None) -> str:
    if not reason:
        return "other"
    return reason.value


def _reason_human_label(reason: str) -> str:
    labels = {
        "performance": "Performance & stability",
        "camera": "Camera quality",
        "battery": "Battery & charging",
        "build_quality": "Build quality & design",
        "price": "Pricing & value",
        "software": "Software experience",
        "connectivity": "Connectivity & audio",
        "customer_support": "Customer support",
        "delivery": "Delivery & packaging",
        "experience": "Overall experience",
        "other": "Miscellaneous feedback",
    }
    return labels.get(reason, reason.title())


def _build_recommendation(reason: str, negative_share: float, sample_quote: str | None) -> Dict:
    action_templates = {
        "performance": "Review recent firmware updates, reproduce lag scenarios and publish a patch roadmap.",
        "camera": "Plan a camera tuning update and share before/after samples to reassure customers.",
        "battery": "Communicate charging best practices and investigate reports of overheating.",
        "build_quality": "Launch a quality inspection campaign and consider proactive replacements for defective units.",
        "price": "Review promotional strategy or bundle added value to justify the price point.",
        "software": "Accelerate the next OxygenOS update and publish a known issues tracker.",
        "connectivity": "Validate antenna and audio calibration, provide troubleshooting guidance.",
        "customer_support": "Improve first-response SLAs and escalate unresolved tickets with a dedicated task force.",
        "delivery": "Audit the logistics partner workflow and send proactive status updates to buyers.",
        "experience": "Launch a satisfaction survey and announce concrete improvements.",
        "other": "Review the detailed comments to identify emerging topics requiring attention.",
    }

    impact_templates = [
        "High visibility issue — resolving it could reduce negative feedback by ~{:.0%}.",
        "Addressing this topic first could recover an estimated {:.0%} of dissatisfied customers.",
        "Quick wins here could improve overall sentiment by around {:.0%}.",
    ]

    impact_msg = impact_templates[int(negative_share * 3) % len(impact_templates)].format(
        min(max(negative_share, 0.1), 0.9)
    )

    return {
        "topic": _reason_human_label(reason),
        "recommended_action": action_templates.get(reason, action_templates["other"]),
        "estimated_impact": impact_msg,
        "sample_quote": sample_quote,
    }


def generate_demo_insights(db: Session) -> Dict:
    mentions: List[Mention] = db.query(Mention).all()
    if not mentions:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "overview": {"message": "No customer feedback found yet."},
            "recommendations": [],
        }

    total = len(mentions)
    positive = [m for m in mentions if m.sentiment == SentimentType.POSITIVE]
    negative = [m for m in mentions if m.sentiment == SentimentType.NEGATIVE]
    neutral = total - len(positive) - len(negative)

    recent_window = datetime.utcnow() - timedelta(days=14)
    recent_mentions = [m for m in mentions if m.published_at >= recent_window]

    reason_counter = Counter(_format_reason(m.reason) for m in mentions)
    negative_counter = Counter(
        _format_reason(m.reason) for m in negative
    )

    recommendations: List[Dict] = []
    for reason, neg_count in negative_counter.most_common(5):
        total_reason_mentions = reason_counter.get(reason, 1)
        negative_share = neg_count / max(total_reason_mentions, 1)
        sample = next(
            (m.content for m in negative if _format_reason(m.reason) == reason and m.content),
            None,
        )
        recommendations.append(_build_recommendation(reason, negative_share, sample))

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "overview": {
            "total_mentions": total,
            "positive": len(positive),
            "neutral": neutral,
            "negative": len(negative),
            "recent_mentions": len(recent_mentions),
        },
        "top_reasons": [
            {
                "reason": _reason_human_label(reason),
                "share": round(count / total * 100, 1),
            }
            for reason, count in reason_counter.most_common(5)
        ],
        "recommendations": recommendations,
    }

