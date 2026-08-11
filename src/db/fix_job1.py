import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("UPDATE jobs SET status='open', last_seen_date=datetime('now') WHERE id=1")
conn.commit()
conn.close()
print("Offre 1 remise a open")