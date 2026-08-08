import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

for job_id in [1, 14, 16]:
    cursor.execute("SELECT title, description FROM jobs WHERE id = ?", (job_id,))
    title, description = cursor.fetchone()
    print(f"--- #{job_id} : {title} ---")
    print(f"Longueur totale : {len(description)} caractères")
    print(f"Caractères 1400-1700 (autour de la coupure) :")
    print(description[1400:1700])
    print()

conn.close()