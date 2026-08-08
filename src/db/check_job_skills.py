import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

JOB_ID = 62  # Digital Transformation Lead, EPC

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT title FROM jobs WHERE id = ?", (JOB_ID,))
title = cursor.fetchone()[0]
print(f"=== Offre #{JOB_ID} : {title} ===\n")

print("SKILLS (compétences minières classées) :")
cursor.execute("""
    SELECT s.skill_name, s.category
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.id
    WHERE js.job_id = ?
""", (JOB_ID,))
for row in cursor.fetchall():
    print(f"  - {row[0]} → {row[1]}")

print("\nOUT_OF_SCOPE (exclues) :")
cursor.execute("SELECT skill_name FROM job_out_of_scope WHERE job_id = ?", (JOB_ID,))
for row in cursor.fetchall():
    print(f"  - {row[0]}")

conn.close()