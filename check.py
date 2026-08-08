import sys
sys.path.append('src')
from db.db import get_connection

conn = get_connection()
c = conn.cursor()

print("=== PROGRESSION ===")
c.execute("SELECT * FROM extraction_progress")
print(c.fetchone())

print("\n=== TOP 10 SKILLS EXTRAITS ===")
c.execute("""
    SELECT s.skill_name, s.category, COUNT(*) as nb
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.id
    GROUP BY s.skill_name
    ORDER BY nb DESC
    LIMIT 10
""")
for row in c.fetchall():
    print(f"  {row[0]} ({row[1]}) : {row[2]} offres")

print("\n=== NOMBRE D'OFFRES AVEC AU MOINS 1 SKILL ===")
c.execute("SELECT COUNT(DISTINCT job_id) FROM job_skills")
print(f"  {c.fetchone()[0]} offres")

print("\n=== TOTAL SKILLS STOCKES ===")
c.execute("SELECT COUNT(*) FROM job_skills")
print(f"  {c.fetchone()[0]} skills")

print("\n=== OUT OF SCOPE ===")
c.execute("SELECT COUNT(*) FROM job_out_of_scope")
print(f"  {c.fetchone()[0]} entrees")

conn.close()
