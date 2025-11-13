"""
Service d'analyse de sentiment utilisant Azure Cognitive Services
"""
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from typing import List, Dict
from models import SentimentType
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.key = os.getenv("AZURE_TEXT_ANALYTICS_KEY")
        self.endpoint = os.getenv("AZURE_TEXT_ANALYTICS_ENDPOINT")
        
        if not self.key or not self.endpoint:
            logger.warning("Azure credentials not configured. Using fallback sentiment analysis.")
            self.client = None
        else:
            try:
                self.client = TextAnalyticsClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.key)
                )
            except Exception as e:
                logger.error(f"Failed to initialize Azure client: {e}")
                self.client = None
    
    def analyze_sentiment(self, text: str, language: str = "fr") -> Dict:
        """
        Analyse le sentiment d'un texte
        Retourne: {sentiment: SentimentType, score: float}
        """
        if self.client:
            try:
                result = self.client.analyze_sentiment(
                    documents=[text],
                    language=language
                )[0]
                
                if result.is_error:
                    logger.error(f"Error analyzing sentiment: {result.error}")
                    return self._fallback_analysis(text)
                
                # Convertir le sentiment Azure en notre enum
                azure_sentiment = result.sentiment.lower()
                if azure_sentiment == "positive":
                    sentiment = SentimentType.POSITIVE
                    score = result.confidence_scores.positive
                elif azure_sentiment == "negative":
                    sentiment = SentimentType.NEGATIVE
                    score = -result.confidence_scores.negative
                else:
                    sentiment = SentimentType.NEUTRAL
                    score = 0.0
                
                return {
                    "sentiment": sentiment,
                    "score": score,
                    "confidence": {
                        "positive": result.confidence_scores.positive,
                        "neutral": result.confidence_scores.neutral,
                        "negative": result.confidence_scores.negative
                    }
                }
            except Exception as e:
                logger.error(f"Error calling Azure API: {e}")
                return self._fallback_analysis(text)
        else:
            return self._fallback_analysis(text)
    
    def _fallback_analysis(self, text: str) -> Dict:
        """
        Analyse de sentiment basique en cas d'absence d'Azure
        Utilise des mots-clés simples
        """
        text_lower = text.lower()
        
        positive_words = ["excellent", "super", "génial", "merci", "bravo", "félicitations", 
                         "parfait", "top", "recommandé", "satisfait", "content", "heureux"]
        negative_words = ["mauvais", "nul", "déçu", "problème", "erreur", "bug", "lent",
                         "cher", "inutile", "décevant", "horrible", "catastrophe", "scandale"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = SentimentType.POSITIVE
            score = min(0.7, 0.3 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = SentimentType.NEGATIVE
            score = max(-0.7, -0.3 - (negative_count * 0.1))
        else:
            sentiment = SentimentType.NEUTRAL
            score = 0.0
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": {
                "positive": 0.5,
                "neutral": 0.5,
                "negative": 0.5
            }
        }
    
    def analyze_batch(self, texts: List[str], language: str = "fr") -> List[Dict]:
        """Analyse le sentiment d'une liste de textes"""
        return [self.analyze_sentiment(text, language) for text in texts]

