# Guide de configuration rapide

## Installation rapide

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp env.example .env
# Éditer .env avec vos clés API
python run.py
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

## Configuration minimale

Pour tester rapidement sans toutes les APIs, vous pouvez laisser les clés API vides. Le système utilisera:
- Analyse de sentiment basique (mots-clés)
- Base de données SQLite (pas de configuration nécessaire)

## Test de l'API

Une fois le backend lancé, accédez à:
- API: http://localhost:8000
- Documentation interactive: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Créer votre première entité

Via l'interface web:
1. Aller sur http://localhost:3000/entities
2. Cliquer sur "Ajouter une entité"
3. Remplir le formulaire (nom, mots-clés)
4. Cliquer sur "Collecter" pour déclencher une collecte

Via l'API:
```bash
curl -X POST "http://localhost:8000/api/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mon Entreprise",
    "keywords": ["produit", "service"],
    "description": "Description de l'entreprise"
  }'
```

## Déclencher une collecte

Via l'interface web:
- Aller sur la page "Entités"
- Cliquer sur le bouton "Collecter" pour une entité

Via l'API:
```bash
curl -X POST "http://localhost:8000/api/collection/trigger" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": 1, "force": false}'
```

