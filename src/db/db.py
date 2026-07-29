import sqlite3
from pathlib import Path

# Chemin vers le fichier de la base de données.
# Path(__file__).parent = le dossier où se trouve CE fichier (src/db/)
# .parent.parent = on remonte de deux niveaux -> la racine du projet
# puis on descend dans data/jobs.db
DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """
    Ouvre une connexion vers le fichier de base de données SQLite.
    Si le fichier n'existe pas encore, SQLite le crée automatiquement.
    """
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """
    Crée la table 'jobs' si elle n'existe pas encore,
    en exécutant le contenu du fichier schema.sql.
    """
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def insert_job(job: dict) -> bool:
    """
    Insère une offre dans la base de données.
    Retourne True si l'offre a bien été insérée (nouvelle offre),
    False si elle existait déjà (doublon détecté et ignoré).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO jobs (external_id, company, title, location, description, url, source, date_scraped)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                job["external_id"],
                job["company"],
                job["title"],
                job["location"],
                job["description"],
                job["url"],
                job["source"],
            ),
        )
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        # Cette erreur se déclenche automatiquement si on essaie d'insérer
        # une ligne qui viole la contrainte UNIQUE(company, external_id)
        # -> ça veut dire que cette offre est déjà en base, on l'ignore simplement
        return False

    finally:
        conn.close()


def count_jobs() -> int:
    """Retourne le nombre total d'offres actuellement en base."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0]
    conn.close()
    return total