"""Ajoute la colonne last_seen_date à la table jobs"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.db"

def add_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifie si la colonne existe déjà (évite une erreur si on relance)
    cursor.execute("PRAGMA table_info(jobs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "last_seen_date" not in columns:
        cursor.execute("ALTER TABLE jobs ADD COLUMN last_seen_date TEXT")
        # Initialise last_seen_date = date_scraped pour toutes les offres existantes
        cursor.execute("UPDATE jobs SET last_seen_date = date_scraped WHERE last_seen_date IS NULL")
        conn.commit()
        print("✅ Colonne last_seen_date ajoutée et initialisée")
    else:
        print("ℹ️  La colonne last_seen_date existe déjà")
    
    conn.close()

if __name__ == "__main__":
    add_column()