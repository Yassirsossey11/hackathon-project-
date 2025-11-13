"""
Router exposing demo AI insights generated locally.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.insights import generate_demo_insights

router = APIRouter()


@router.get("/demo")
async def get_demo_insights(db: Session = Depends(get_db)):
    """
    Return synthetic AI-like insights to showcase the assistant without
    relying on external APIs.
    """
    return generate_demo_insights(db)

