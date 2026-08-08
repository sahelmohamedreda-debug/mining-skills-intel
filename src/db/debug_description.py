import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

# Vérifie que les descriptions sont bien différentes en base
for job_id in [1, 14, 16]:
    cursor.execute("SELECT title, description FROM jobs WHERE id = ?", (job_id,))
    title, description = cursor.fetchone()
    print(f"--- #{job_id} : {title} ---")
    print(f"Description (100 premiers caractères) : {description[:100]}")
    print()

conn.close()