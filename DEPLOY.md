# Guide de déploiement sur Vercel

Ce guide explique comment déployer l'application sur Vercel.

## Prérequis

1. Un compte Vercel (gratuit) : https://vercel.com
2. Git installé sur votre machine
3. Le projet doit être poussé sur GitHub, GitLab ou Bitbucket

## Configuration de la base de données

⚠️ **Important** : Vercel ne supporte pas SQLite de manière persistante. Vous devez utiliser une base de données externe.

### Option 1 : Vercel Postgres (Recommandé)

1. Dans votre projet Vercel, allez dans l'onglet "Storage"
2. Créez une nouvelle base de données Postgres
3. Copiez la variable d'environnement `POSTGRES_URL` qui sera automatiquement créée

### Option 2 : Base de données externe

Utilisez un service comme :
- Supabase (gratuit)
- Railway (gratuit)
- Neon (gratuit)
- Render (gratuit)

## Variables d'environnement à configurer

Dans votre projet Vercel, allez dans **Settings > Environment Variables** et ajoutez :

1. **POSTGRES_URL** (si vous utilisez Vercel Postgres) : Automatiquement créée par Vercel
   - Le code détecte automatiquement cette variable et l'utilise
   - Pas besoin de configurer manuellement

2. **DATABASE_URL** (si vous utilisez une base de données externe) : L'URL de votre base de données PostgreSQL
   - Format : `postgresql://user:password@host:port/database`
   - Note : Si `POSTGRES_URL` est disponible, elle sera utilisée en priorité

3. **REACT_APP_API_BASE_URL** (optionnel) : L'URL de votre API
   - En production, le frontend utilise automatiquement `/api` (URL relative)
   - Vous pouvez définir cette variable si vous voulez utiliser une URL absolue
   - Format : `https://votre-projet.vercel.app/api`

4. Autres variables d'environnement nécessaires (clés API Azure, Twitter, Reddit, NewsAPI, etc.)

## Déploiement

### Méthode 1 : Via l'interface Vercel (Recommandé)

1. Allez sur https://vercel.com
2. Cliquez sur "Add New Project"
3. Importez votre repository GitHub/GitLab/Bitbucket
4. Vercel détectera automatiquement la configuration
5. Configurez les variables d'environnement
6. Cliquez sur "Deploy"

### Méthode 2 : Via la CLI Vercel

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer
vercel

# Pour la production
vercel --prod
```

## Configuration du frontend

Le frontend React sera automatiquement détecté et déployé. Le fichier `vercel.json` configure :
- Le build du frontend depuis `frontend/package.json`
- Le répertoire de sortie `frontend/build`
- Les routes pour servir les fichiers statiques et l'API

**Note** : En production, le frontend utilise automatiquement l'URL relative `/api` pour communiquer avec le backend. Aucune configuration supplémentaire n'est nécessaire.

## Configuration du backend

Le backend FastAPI est configuré pour fonctionner comme une fonction serverless via :
- `api/index.py` : Point d'entrée pour Vercel
- `mangum` : Adaptateur ASGI pour AWS Lambda/Vercel

## Structure des fichiers

```
.
├── api/
│   ├── index.py          # Point d'entrée pour l'API
│   └── requirements.txt  # Dépendances Python pour Vercel
├── backend/              # Code source du backend
├── frontend/             # Code source du frontend
├── vercel.json          # Configuration Vercel
└── .vercelignore        # Fichiers à ignorer
```

## Vérification après déploiement

1. Vérifiez que l'API fonctionne : `https://votre-projet.vercel.app/api/health`
2. Vérifiez que le frontend fonctionne : `https://votre-projet.vercel.app`
3. Testez les endpoints de l'API

## Dépannage

### Erreur de connexion à la base de données

- Pour Vercel Postgres : Vérifiez que la base de données est créée dans l'onglet "Storage" de Vercel
  - La variable `POSTGRES_URL` est automatiquement disponible
  - Le code détecte automatiquement cette variable
- Pour une base de données externe : Vérifiez que `DATABASE_URL` est correctement configurée
- Assurez-vous que la base de données accepte les connexions depuis Vercel (whitelist IP si nécessaire)
- Vérifiez que l'URL de la base de données utilise le format `postgresql://` (pas `postgres://`)

### Erreur CORS

- Vérifiez que les origines sont correctement configurées dans `backend/main.py`
- Le domaine Vercel est automatiquement ajouté aux origines autorisées

### Erreur de build

- Vérifiez les logs de build dans Vercel
- Assurez-vous que toutes les dépendances sont dans `api/requirements.txt`
- Vérifiez que le chemin vers le backend est correct dans `api/index.py`

## Notes importantes

- Les fonctions serverless Vercel ont une limite de temps d'exécution (10 secondes pour le plan gratuit)
- La base de données doit être externe (pas de SQLite)
- Les fichiers statiques doivent être dans `frontend/build` après le build

