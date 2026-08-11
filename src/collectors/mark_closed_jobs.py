"""
Marque comme 'closed' toutes les offres qui n'ont pas été revues
lors de la dernière exécution de collecte.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.db"

HOURS_THRESHOLD = 24

def get_connection():
    return sqlite3.connect(DB_PATH)

def mark_closed_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, company, last_seen_date
        FROM jobs
        WHERE status = 'open'
        AND datetime(last_seen_date) < datetime('now', ?)
    """, (f'-{HOURS_THRESHOLD} hours',))
    
    stale_jobs = cursor.fetchall()
    
    if not stale_jobs:
        print("Aucune offre a fermer - tout est a jour")
        conn.close()
        return
    
    print(f"{len(stale_jobs)} offre(s) a marquer comme 'closed' :")
    for job_id, title, company, last_seen in stale_jobs:
        print(f"   #{job_id} [{company}] {title} (vue pour la derniere fois : {last_seen})")
    
    cursor.execute("""
        UPDATE jobs SET status = 'closed'
        WHERE status = 'open'
        AND datetime(last_seen_date) < datetime('now', ?)
    """, (f'-{HOURS_THRESHOLD} hours',))
    
    conn.commit()
    print(f"{cursor.rowcount} offre(s) marquee(s) comme fermee(s)")
    conn.close()

if __name__ == "__main__":
    mark_closed_jobs()