# Analyse Automatisée de la Réputation en Ligne

Solution complète d'analyse de réputation automatisée combinant IA et sources OSINT pour le suivi de l'image publique des entreprises.

## 🎯 Fonctionnalités

- **Collecte automatique** de données depuis la presse, réseaux sociaux et web
- **Analyse de sentiment** automatique (positif, neutre, négatif) via Azure Cognitive Services
- **Tableau de bord visuel** avec scores de réputation, tendances et alertes
- **Intégration Microsoft** (Power Automate, Azure Cognitive Services, Logic Apps)
- **Système d'alertes** pour détecter les crises et mentions négatives en temps réel

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: React avec visualisations interactives
- **Base de données**: PostgreSQL/SQLite
- **IA**: Azure Cognitive Services (Text Analytics)
- **APIs OSINT**: NewsAPI, Twitter API, Reddit API, etc.

## 🚀 Installation

### Prérequis

- Python 3.9+
- Node.js 16+
- Compte Azure avec Cognitive Services activé
- Clés API pour les services OSINT

### Configuration

1. Cloner le projet
2. Installer les dépendances backend:
```bash
cd backend
pip install -r requirements.txt
```

3. Installer les dépendances frontend:
```bash
cd frontend
npm install
```

4. Configurer les variables d'environnement:
```bash
cd backend
cp env.example .env
# Éditer .env avec vos clés API
```

5. Lancer le backend:
```bash
cd backend
uvicorn main:app --reload
```
Le backend sera accessible sur `http://localhost:8000`
Documentation API: `http://localhost:8000/docs`

6. Lancer le frontend (dans un nouveau terminal):
```bash
cd frontend
npm install
npm start
```
Le frontend sera accessible sur `http://localhost:3000`
## 📊 Utilisation

1. Accéder au tableau de bord: `http://localhost:3000`
2. Configurer les entités à surveiller (nom d'entreprise, mots-clés)
3. Le système collecte automatiquement les mentions
4. Visualiser les scores de réputation et tendances
5. Recevoir des alertes pour les mentions critiques

## 🔧 Configuration des APIs

### Azure Cognitive Services (Text Analytics)

1. Créer une ressource Azure Cognitive Services (Text Analytics)
2. Obtenir la clé API et l'endpoint
3. Configurer dans `backend/.env`:
```
AZURE_TEXT_ANALYTICS_KEY=your_key
AZURE_TEXT_ANALYTICS_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

**Note:** Si Azure n'est pas configuré, le système utilisera une analyse de sentiment basique basée sur des mots-clés.

### APIs OSINT

#### NewsAPI
1. Obtenir une clé gratuite sur [newsapi.org](https://newsapi.org/)
2. Configurer dans `backend/.env`:
```
NEWSAPI_KEY=your_newsapi_key
```

#### Twitter API
1. Créer une application sur [developer.twitter.com](https://developer.twitter.com/)
2. Obtenir un Bearer Token
3. Configurer dans `backend/.env`:
```
TWITTER_BEARER_TOKEN=your_bearer_token
```

#### Reddit API
1. Créer une application sur [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Obtenir Client ID et Client Secret
3. Configurer dans `backend/.env`:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=ReputationAnalyzer/1.0
```

## 🔄 Collecte automatique

Pour activer la collecte automatique périodique, vous pouvez utiliser le scheduler:

```bash
cd backend
python services/scheduler.py
```

Par défaut, la collecte s'exécute toutes les 6 heures. Vous pouvez également déclencher une collecte manuelle via l'API ou l'interface web.

## 📁 Structure du projet

```
hackthon/
├── backend/
│   ├── routers/          # Routes API
│   ├── services/         # Services métier
│   ├── models.py         # Modèles de données
│   ├── schemas.py        # Schémas Pydantic
│   ├── database.py       # Configuration DB
│   ├── main.py           # Application FastAPI
│   └── requirements.txt  # Dépendances Python
├── frontend/
│   ├── src/
│   │   ├── components/   # Composants React
│   │   ├── services/     # Services API
│   │   └── App.js        # Application principale
│   └── package.json      # Dépendances Node
└── README.md
```

## 🎯 Fonctionnalités principales

### 1. Gestion des entités
- Ajouter/modifier/supprimer des entités à surveiller
- Configurer des mots-clés de recherche
- Activer/désactiver la surveillance

### 2. Collecte de données
- Collecte automatique depuis multiples sources (presse, réseaux sociaux, web)
- Support de NewsAPI, Twitter, Reddit
- Détection automatique des doublons

### 3. Analyse de sentiment
- Analyse via Azure Cognitive Services
- Classification: positif, neutre, négatif
- Score de confiance pour chaque mention

### 4. Tableau de bord
- Vue d'ensemble des statistiques
- Graphiques de répartition des sentiments
- Scores de réputation par entité
- Tendances (amélioration, stabilité, déclin)

### 5. Système d'alertes
- Alertes automatiques pour mentions négatives
- Niveaux de gravité: critique, élevé, moyen
- Détection de mots-clés critiques
- Interface de gestion des alertes

## 🚨 Dépannage

### Le backend ne démarre pas
- Vérifier que Python 3.9+ est installé
- Vérifier que toutes les dépendances sont installées: `pip install -r requirements.txt`
- Vérifier que le fichier `.env` existe et est correctement configuré

### Le frontend ne se connecte pas au backend
- Vérifier que le backend est lancé sur le port 8000
- Vérifier la configuration CORS dans `backend/main.py`
- Vérifier le proxy dans `frontend/package.json`

### Erreurs de collecte de données
- Vérifier que les clés API sont correctement configurées
- Vérifier les limites de taux des APIs (rate limiting)
- Consulter les logs du backend pour plus de détails

## 📝 Licence

MIT

