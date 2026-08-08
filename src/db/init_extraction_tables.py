"""Initialise les tables pour l'extraction des compétences"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.db"

def init_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crée les tables
    sql_commands = [
        """CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Operational & Technical', 'Health, Safety & Risk Management', 'Digital & Automation', 'Soft & Leadership')),
            compliance_relevant BOOLEAN DEFAULT FALSE,
            UNIQUE(skill_name, category)
        );""",
        
        """CREATE TABLE IF NOT EXISTS job_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            FOREIGN KEY(job_id) REFERENCES jobs(id),
            FOREIGN KEY(skill_id) REFERENCES skills(id),
            UNIQUE(job_id, skill_id)
        );""",
        
        """CREATE TABLE IF NOT EXISTS job_out_of_scope (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            FOREIGN KEY(job_id) REFERENCES jobs(id),
            UNIQUE(job_id, skill_name)
        );""",
        
        """CREATE TABLE IF NOT EXISTS extraction_progress (
            id INTEGER PRIMARY KEY,
            last_processed_job_id INTEGER DEFAULT 0,
            total_processed INTEGER DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        );""",
        
        "INSERT OR IGNORE INTO extraction_progress (id) VALUES (1);"
    ]
    
    for sql in sql_commands:
        cursor.execute(sql)
    
    conn.commit()
    
    # Vérifie les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%skill%' OR name='extraction_progress' OR name='job_out_of_scope')")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("✅ Tables créées :")
    for table in tables:
        print(f"   - {table}")
    
    conn.close()

if __name__ == "__main__":
    init_tables()