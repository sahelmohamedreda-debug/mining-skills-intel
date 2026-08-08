import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

print("=" * 60)
print("VÉRIFICATION COMPLÈTE DE L'EXTRACTION")
print("=" * 60)

# 1. Progression générale
print("\n1. PROGRESSION")
cursor.execute("SELECT last_processed_job_id, total_processed FROM extraction_progress WHERE id = 1")
last_id, total = cursor.fetchone()
cursor.execute("SELECT COUNT(*) FROM jobs")
total_jobs = cursor.fetchone()[0]
print(f"   Dernier ID traité : {last_id} / {total_jobs}")
print(f"   Offres traitées : {total}")
print(f"   Restantes : {total_jobs - last_id}")

# 2. Cohérence : chaque offre traitée a-t-elle bien été enregistrée quelque part ?
print("\n2. COHÉRENCE (offres traitées avec 0 résultat)")
cursor.execute("""
    SELECT j.id, j.title
    FROM jobs j
    WHERE j.id <= ?
    AND j.id NOT IN (SELECT DISTINCT job_id FROM job_skills)
    AND j.id NOT IN (SELECT DISTINCT job_id FROM job_out_of_scope)
""", (last_id,))
empty_jobs = cursor.fetchall()
if empty_jobs:
    print(f"   ⚠️  {len(empty_jobs)} offres traitées SANS aucune donnée stockée :")
    for job_id, title in empty_jobs[:10]:
        print(f"      #{job_id} : {title}")
else:
    print("   ✅ Toutes les offres traitées ont au moins une donnée stockée")

# 3. Statistiques skills
print("\n3. STATISTIQUES SKILLS")
cursor.execute("SELECT COUNT(*) FROM skills")
print(f"   Compétences uniques : {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM job_skills")
print(f"   Total liens offre-compétence : {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(DISTINCT job_id) FROM job_skills")
print(f"   Offres avec au moins 1 compétence : {cursor.fetchone()[0]}")

# 4. Statistiques out_of_scope
print("\n4. STATISTIQUES OUT_OF_SCOPE")
cursor.execute("SELECT COUNT(*) FROM job_out_of_scope")
print(f"   Total entrées : {cursor.fetchone()[0]}")

# 5. Répartition par catégorie
print("\n5. RÉPARTITION PAR CATÉGORIE")
cursor.execute("""
    SELECT category, COUNT(DISTINCT s.id) as nb_skills, COUNT(js.id) as nb_liens
    FROM skills s
    LEFT JOIN job_skills js ON s.id = js.skill_id
    GROUP BY category
    ORDER BY nb_liens DESC
""")
for row in cursor.fetchall():
    print(f"   {row[0]} : {row[1]} compétences distinctes, {row[2]} occurrences totales")

# 6. Compliance relevant
print("\n6. COMPLIANCE RELEVANT")
cursor.execute("SELECT COUNT(*) FROM skills WHERE compliance_relevant = 1")
print(f"   Compétences marquées compliance_relevant=true : {cursor.fetchone()[0]}")

# 7. Échantillon de 3 offres avec leurs compétences (vérification visuelle)
print("\n7. ÉCHANTILLON DE VÉRIFICATION (3 offres)")
cursor.execute("SELECT id, title FROM jobs WHERE id <= ? ORDER BY RANDOM() LIMIT 3", (last_id,))
sample_jobs = cursor.fetchall()
for job_id, title in sample_jobs:
    print(f"\n   --- #{job_id} : {title} ---")
    cursor.execute("""
        SELECT s.skill_name, s.category
        FROM job_skills js JOIN skills s ON js.skill_id = s.id
        WHERE js.job_id = ?
    """, (job_id,))
    skills = cursor.fetchall()
    if skills:
        for skill_name, category in skills:
            print(f"      ✓ {skill_name} ({category})")
    else:
        print("      (aucune compétence)")

conn.close()
print("\n" + "=" * 60)
print("VÉRIFICATION TERMINÉE")
print("=" * 60)