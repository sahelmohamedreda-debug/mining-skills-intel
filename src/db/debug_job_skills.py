import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

print("=== Contenu brut de job_skills (job_id, skill_id) ===")
cursor.execute("SELECT job_id, skill_id FROM job_skills ORDER BY job_id LIMIT 30")
for row in cursor.fetchall():
    print(row)

print("\n=== Nombre de job_id DISTINCTS dans job_skills ===")
cursor.execute("SELECT COUNT(DISTINCT job_id) FROM job_skills")
print(cursor.fetchone()[0])

print("\n=== Tous les job_id présents ===")
cursor.execute("SELECT DISTINCT job_id FROM job_skills ORDER BY job_id")
for row in cursor.fetchall():
    print(row[0])

conn.close()