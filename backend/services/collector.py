"""
Service de collecte de données depuis diverses sources OSINT
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup
import time

from models import Entity, Mention, SourceType
from services.sentiment_analyzer import SentimentAnalyzer
from services.alert_service import AlertService
from services.reason_classifier import determine_reason

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self, db: Session):
        self.db = db
        self.sentiment_analyzer = SentimentAnalyzer()
        self.alert_service = AlertService(db)
        
        # Configuration des APIs
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = os.getenv("REDDIT_USER_AGENT", "ReputationAnalyzer/1.0")
    
    def collect_for_entity(self, entity_id: int, force: bool = False):
        """Collecter les données pour une entité"""
        try:
            entity = self.db.query(Entity).filter(Entity.id == entity_id).first()
            if not entity:
                logger.error(f"Entity {entity_id} not found")
                return
            
            keywords = json.loads(entity.keywords) if isinstance(entity.keywords, str) else entity.keywords
            search_terms = [entity.name] + keywords
            
            logger.info(f"Starting collection for entity: {entity.name}")
            
            # Collecter depuis différentes sources
            mentions_count = 0
            
            # 1. Collecte depuis NewsAPI
            if self.newsapi_key:
                mentions_count += self._collect_from_news(search_terms, entity_id, force)
            
            # 2. Collecte depuis Twitter (si configuré)
            if self.twitter_bearer_token:
                mentions_count += self._collect_from_twitter(search_terms, entity_id, force)
            
            # 3. Collecte depuis Reddit (si configuré)
            if self.reddit_client_id and self.reddit_client_secret:
                mentions_count += self._collect_from_reddit(search_terms, entity_id, force)
            
            # 4. Collecte web générique (scraping basique)
            mentions_count += self._collect_from_web(search_terms, entity_id, force)
            
            logger.info(f"Collection completed for {entity.name}: {mentions_count} new mentions")
            
        except Exception as e:
            logger.error(f"Error collecting data for entity {entity_id}: {e}")
    
    def _collect_from_news(self, search_terms: List[str], entity_id: int, force: bool) -> int:
        """Collecter depuis NewsAPI"""
        if not self.newsapi_key:
            return 0
        
        count = 0
        try:
            for term in search_terms[:3]:  # Limiter à 3 termes pour éviter les limites API
                url = "https://newsapi.org/v2/everything"
                params = {
                    "q": term,
                    "language": "fr",
                    "sortBy": "publishedAt",
                    "pageSize": 20,
                    "apiKey": self.newsapi_key
                }
                
                if not force:
                    # Ne récupérer que les articles des 7 derniers jours
                    params["from"] = (datetime.utcnow() - timedelta(days=7)).isoformat()
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    
                    for article in articles:
                        if self._save_mention(
                            entity_id=entity_id,
                            content=article.get("title", "") + " " + article.get("description", ""),
                            source=SourceType.NEWS,
                            source_url=article.get("url"),
                            author=article.get("source", {}).get("name"),
                            published_at=self._parse_date(article.get("publishedAt"))
                        ):
                            count += 1
                
                time.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Error collecting from NewsAPI: {e}")
        
        return count
    
    def _collect_from_twitter(self, search_terms: List[str], entity_id: int, force: bool) -> int:
        """Collecter depuis Twitter API v2"""
        if not self.twitter_bearer_token:
            return 0
        
        count = 0
        try:
            headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
            
            for term in search_terms[:2]:  # Limiter pour éviter les limites
                url = "https://api.twitter.com/2/tweets/search/recent"
                params = {
                    "query": f"{term} lang:fr",
                    "max_results": 20,
                    "tweet.fields": "created_at,author_id,public_metrics"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get("data", [])
                    
                    for tweet in tweets:
                        if self._save_mention(
                            entity_id=entity_id,
                            content=tweet.get("text", ""),
                            source=SourceType.TWITTER,
                            source_url=f"https://twitter.com/i/web/status/{tweet.get('id')}",
                            author=f"user_{tweet.get('author_id')}",
                            published_at=self._parse_date(tweet.get("created_at"))
                        ):
                            count += 1
                
                time.sleep(1)  # Rate limiting Twitter
                
        except Exception as e:
            logger.error(f"Error collecting from Twitter: {e}")
        
        return count
    
    def _collect_from_reddit(self, search_terms: List[str], entity_id: int, force: bool) -> int:
        """Collecter depuis Reddit API"""
        if not self.reddit_client_id or not self.reddit_client_secret:
            return 0
        
        count = 0
        try:
            # Authentification Reddit
            auth = requests.auth.HTTPBasicAuth(self.reddit_client_id, self.reddit_client_secret)
            data = {
                "grant_type": "client_credentials"
            }
            headers = {"User-Agent": self.reddit_user_agent}
            
            response = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning("Failed to authenticate with Reddit")
                return 0
            
            token = response.json().get("access_token")
            headers = {"Authorization": f"bearer {token}", "User-Agent": self.reddit_user_agent}
            
            for term in search_terms[:2]:
                url = f"https://oauth.reddit.com/search"
                params = {
                    "q": term,
                    "limit": 20,
                    "sort": "new"
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    
                    for post_data in posts:
                        post = post_data.get("data", {})
                        if self._save_mention(
                            entity_id=entity_id,
                            content=post.get("title", "") + " " + post.get("selftext", ""),
                            source=SourceType.REDDIT,
                            source_url=f"https://reddit.com{post.get('permalink', '')}",
                            author=post.get("author"),
                            published_at=datetime.fromtimestamp(post.get("created_utc", 0))
                        ):
                            count += 1
                
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error collecting from Reddit: {e}")
        
        return count
    
    def _collect_from_web(self, search_terms: List[str], entity_id: int, force: bool) -> int:
        """Collecte web générique (exemple simplifié)"""
        # Cette méthode est un exemple basique
        # En production, utiliser un service de scraping plus robuste
        count = 0
        try:
            # Exemple: recherche Google News (scraping basique)
            # Note: En production, utiliser l'API Google News ou un service dédié
            for term in search_terms[:1]:
                # Placeholder pour scraping web
                # Dans un vrai projet, utiliser Scrapy, Selenium, ou un service API
                pass
        except Exception as e:
            logger.error(f"Error collecting from web: {e}")
        
        return count
    
    def _save_mention(
        self,
        entity_id: int,
        content: str,
        source: SourceType,
        source_url: Optional[str],
        author: Optional[str],
        published_at: datetime
    ) -> bool:
        """Sauvegarder une mention dans la base de données"""
        try:
            # Vérifier si la mention existe déjà (éviter les doublons)
            existing = self.db.query(Mention).filter(
                Mention.entity_id == entity_id,
                Mention.source_url == source_url,
                Mention.source == source
            ).first()
            
            if existing:
                return False
            
            # Analyser le sentiment
            analysis = self.sentiment_analyzer.analyze_sentiment(content)
            reason_enum, reason_detail = determine_reason(content)
            
            # Créer la mention
            mention = Mention(
                entity_id=entity_id,
                content=content[:5000],  # Limiter la longueur
                source=source,
                source_url=source_url,
                author=author,
                sentiment=analysis["sentiment"],
                sentiment_score=analysis["score"],
                reason=reason_enum,
                reason_detail=reason_detail,
                published_at=published_at,
                language="fr"
            )
            
            self.db.add(mention)
            self.db.commit()
            self.db.refresh(mention)
            
            # Vérifier si une alerte doit être créée
            self.alert_service.check_and_create_alert(mention)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving mention: {e}")
            self.db.rollback()
            return False
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parser une date depuis une chaîne"""
        if not date_str:
            return datetime.utcnow()
        
        try:
            # Formats communs
            for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S"]:
                try:
                    return datetime.strptime(date_str.replace("+00:00", "").replace("Z", ""), fmt)
                except:
                    continue
        except:
            pass
        
        return datetime.utcnow()

