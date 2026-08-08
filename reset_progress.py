import sys
sys.path.append('src')
from db.db import get_connection

conn = get_connection()
c = conn.cursor()

c.execute("UPDATE extraction_progress SET last_processed_job_id = 10, total_processed = 10 WHERE id = 1")

c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = c.fetchall()
print("Tables dans la DB :")
for t in tables:
    print(f"  - {t[0]}")

c.execute("SELECT * FROM extraction_progress")
progress = c.fetchone()
print(f"Progression : last_id={progress[1]}, total={progress[2]}")

c.execute("SELECT COUNT(*) FROM job_skills")
print(f"Skills extraits : {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM job_out_of_scope")
print(f"Out-of-scope : {c.fetchone()[0]}")

conn.commit()
conn.close()
print("Fait !")
