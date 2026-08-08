import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

print("=== STATISTIQUES GÉNÉRALES ===")
cursor.execute("SELECT COUNT(DISTINCT job_id) FROM job_skills")
print(f"Offres avec au moins 1 compétence : {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM job_skills")
print(f"Total liens offre-compétence : {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(DISTINCT skill_name) FROM skills")
print(f"Compétences uniques : {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM job_out_of_scope")
print(f"Entrées out_of_scope : {cursor.fetchone()[0]}")

print("\n=== TOP 15 COMPÉTENCES LES PLUS FRÉQUENTES ===")
cursor.execute("""
    SELECT s.skill_name, s.category, COUNT(*) as nb
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.id
    GROUP BY s.skill_name
    ORDER BY nb DESC
    LIMIT 15
""")
for row in cursor.fetchall():
    print(f"  {row[0]} ({row[1]}) : {row[2]} offres")

print("\n=== RÉPARTITION PAR CATÉGORIE ===")
cursor.execute("""
    SELECT category, COUNT(*) as nb
    FROM skills
    GROUP BY category
    ORDER BY nb DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0]} : {row[1]} compétences distinctes")

print("\n=== EXEMPLE : COMPÉTENCES D'UNE OFFRE SPÉCIFIQUE ===")
cursor.execute("""
    SELECT j.title, s.skill_name, s.category
    FROM job_skills js
    JOIN jobs j ON js.job_id = j.id
    JOIN skills s ON js.skill_id = s.id
    WHERE j.id = 32
""")
for row in cursor.fetchall():
    print(f"  [{row[0]}] {row[1]} → {row[2]}")

conn.close()