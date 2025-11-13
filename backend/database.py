"""
Configuration de la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Vercel Postgres utilise POSTGRES_URL, convertir en DATABASE_URL si nécessaire
postgres_url = os.getenv("POSTGRES_URL")
if postgres_url:
    # Convertir POSTGRES_URL en format SQLAlchemy si nécessaire
    if postgres_url.startswith("postgres://"):
        # Convertir postgres:// en postgresql:// pour SQLAlchemy
        DATABASE_URL = postgres_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = postgres_url
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reputation.db")

# S'assurer que l'URL SQLite est correcte
if DATABASE_URL and not DATABASE_URL.startswith("sqlite://") and not DATABASE_URL.startswith("postgresql://"):
    # Si ce n'est pas un format valide, utiliser la valeur par défaut
    DATABASE_URL = "sqlite:///./reputation.db"

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

