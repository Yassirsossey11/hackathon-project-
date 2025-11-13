# Architecture de la Solution

## Vue d'ensemble

Cette solution d'analyse automatisée de réputation en ligne est construite avec une architecture moderne en deux parties: un backend API REST et un frontend React.

## Backend (FastAPI)

### Structure

```
backend/
├── main.py                 # Point d'entrée de l'application
├── database.py             # Configuration SQLAlchemy
├── models.py               # Modèles de données (Entity, Mention, Alert)
├── schemas.py              # Schémas Pydantic pour validation
├── routers/                # Routes API organisées par domaine
│   ├── entities.py         # Gestion des entités
│   ├── mentions.py         # Gestion des mentions
│   ├── alerts.py           # Gestion des alertes
│   ├── dashboard.py        # Statistiques et tableaux de bord
│   └── collection.py       # Déclenchement de collecte
└── services/               # Logique métier
    ├── collector.py        # Collecte de données OSINT
    ├── sentiment_analyzer.py  # Analyse de sentiment (Azure)
    ├── alert_service.py    # Gestion des alertes
    └── scheduler.py        # Planification automatique
```

### Flux de données

1. **Collecte** → `DataCollector` récupère les données depuis:
   - NewsAPI (presse)
   - Twitter API (réseaux sociaux)
   - Reddit API (forums)
   - Web scraping (générique)

2. **Analyse** → `SentimentAnalyzer` analyse chaque mention:
   - Utilise Azure Cognitive Services si configuré
   - Fallback sur analyse basique par mots-clés

3. **Stockage** → Les mentions sont sauvegardées dans la base de données

4. **Alertes** → `AlertService` vérifie et crée des alertes si nécessaire:
   - Sentiment très négatif → Alerte critique
   - Mots-clés critiques → Alerte élevée
   - Sentiment négatif modéré → Alerte moyenne

5. **Visualisation** → Les données sont exposées via l'API REST

## Frontend (React)

### Structure

```
frontend/
├── src/
│   ├── App.js              # Application principale avec routing
│   ├── components/
│   │   ├── Layout.js       # Layout avec navigation
│   │   ├── Dashboard.js    # Tableau de bord principal
│   │   ├── Entities.js     # Gestion des entités
│   │   ├── Mentions.js     # Liste des mentions
│   │   └── Alerts.js       # Gestion des alertes
│   └── services/
│       └── api.js          # Client API Axios
```

### Composants principaux

- **Dashboard**: Vue d'ensemble avec statistiques et graphiques
- **Entities**: CRUD pour les entités à surveiller
- **Mentions**: Liste filtrée des mentions collectées
- **Alerts**: Gestion des alertes avec résolution

## Base de données

### Modèles

1. **Entity**: Entités surveillées (entreprises, marques)
   - name, keywords, description, is_active

2. **Mention**: Mentions collectées
   - entity_id, content, source, sentiment, sentiment_score, published_at

3. **Alert**: Alertes générées
   - mention_id, severity, message, is_resolved

## Intégrations

### Azure Cognitive Services
- **Text Analytics API**: Analyse de sentiment avancée
- Fallback automatique si non configuré

### APIs OSINT
- **NewsAPI**: Articles de presse
- **Twitter API v2**: Tweets récents
- **Reddit API**: Posts et commentaires

## Sécurité

- Variables d'environnement pour les clés API
- CORS configuré pour le frontend
- Validation des données avec Pydantic
- Protection contre les doublons de mentions

## Performance

- Collecte asynchrone en arrière-plan
- Pagination des résultats
- Cache possible pour les statistiques
- Rate limiting respecté pour les APIs externes

## Extensibilité

La solution est conçue pour être facilement extensible:

- Ajout de nouvelles sources de données dans `collector.py`
- Nouveaux types d'alertes dans `alert_service.py`
- Nouveaux graphiques dans `Dashboard.js`
- Intégration Power Automate/Logic Apps possible via webhooks

