"""
Script pour initialiser la base de données
"""
from database import engine, Base
from models import Entity, Mention, Alert

def init_database():
    """Créer toutes les tables de la base de données"""
    print("Création des tables de la base de données...")
    Base.metadata.create_all(bind=engine)
    print("✓ Base de données initialisée avec succès!")
    print("Fichier: reputation.db")

if __name__ == "__main__":
    init_database()

