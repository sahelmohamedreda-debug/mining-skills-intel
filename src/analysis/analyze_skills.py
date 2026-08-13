import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from db.db import get_connection

conn = get_connection()

print("=" * 70)
print("ANALYSE DES COMPÉTENCES MINIÈRES — JOUR 15")
print("=" * 70)

# ============================================================
# 1. VUE D'ENSEMBLE
# ============================================================
print("\n1. VUE D'ENSEMBLE\n")

total_jobs = pd.read_sql("SELECT COUNT(*) as n FROM jobs", conn).iloc[0]["n"]
jobs_with_skills = pd.read_sql(
    "SELECT COUNT(DISTINCT job_id) as n FROM job_skills", conn
).iloc[0]["n"]
total_skills_links = pd.read_sql("SELECT COUNT(*) as n FROM job_skills", conn).iloc[0]["n"]

print(f"Total offres collectées      : {total_jobs}")
print(f"Offres avec compétences      : {jobs_with_skills} ({jobs_with_skills/total_jobs*100:.1f}%)")
print(f"Total liens offre-compétence : {total_skills_links}")

# ============================================================
# 2. TOP 10 COMPÉTENCES GLOBALES
# ============================================================
print("\n" + "=" * 70)
print("2. TOP 10 COMPÉTENCES LES PLUS DEMANDÉES (toutes catégories)")
print("=" * 70 + "\n")

top_skills = pd.read_sql("""
    SELECT s.skill_name, s.category, COUNT(*) as nb_offres
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.id
    GROUP BY s.skill_name
    ORDER BY nb_offres DESC
    LIMIT 10
""", conn)
print(top_skills.to_string(index=False))

# ============================================================
# 3. RÉPARTITION PAR CATÉGORIE
# ============================================================
print("\n" + "=" * 70)
print("3. RÉPARTITION DES COMPÉTENCES PAR CATÉGORIE")
print("=" * 70 + "\n")

by_category = pd.read_sql("""
    SELECT s.category,
           COUNT(DISTINCT s.id) as competences_uniques,
           COUNT(js.id) as occurrences_totales,
           COUNT(DISTINCT js.job_id) as offres_concernees
    FROM skills s
    LEFT JOIN job_skills js ON s.id = js.skill_id
    GROUP BY s.category
    ORDER BY occurrences_totales DESC
""", conn)
by_category["pct_offres"] = (by_category["offres_concernees"] / jobs_with_skills * 100).round(1)
print(by_category.to_string(index=False))

# ============================================================
# 4. RÉPARTITION PAR ENTREPRISE
# ============================================================
print("\n" + "=" * 70)
print("4. NOMBRE D'OFFRES ET DE COMPÉTENCES PAR ENTREPRISE")
print("=" * 70 + "\n")

by_company = pd.read_sql("""
    SELECT j.company,
           COUNT(DISTINCT j.id) as nb_offres,
           COUNT(js.id) as nb_competences_extraites
    FROM jobs j
    LEFT JOIN job_skills js ON j.id = js.job_id
    GROUP BY j.company
    ORDER BY nb_offres DESC
""", conn)
print(by_company.to_string(index=False))

# ============================================================
# 5. RÉPARTITION PAR LOCALISATION (top 10)
# ============================================================
print("\n" + "=" * 70)
print("5. TOP 10 LOCALISATIONS (nombre d'offres)")
print("=" * 70 + "\n")

by_location = pd.read_sql("""
    SELECT location, COUNT(*) as nb_offres
    FROM jobs
    WHERE location IS NOT NULL AND location != ''
    GROUP BY location
    ORDER BY nb_offres DESC
    LIMIT 10
""", conn)
print(by_location.to_string(index=False))

# ============================================================
# 6. COMPLIANCE RELEVANT
# ============================================================
print("\n" + "=" * 70)
print("6. COMPÉTENCES LIÉES À LA CONFORMITÉ (compliance_relevant)")
print("=" * 70 + "\n")

compliance = pd.read_sql("""
    SELECT s.skill_name, s.category, COUNT(*) as nb_offres
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.id
    WHERE s.compliance_relevant = 1
    GROUP BY s.skill_name
    ORDER BY nb_offres DESC
    LIMIT 10
""", conn)
if len(compliance) > 0:
    print(compliance.to_string(index=False))
else:
    print("Aucune compétence compliance_relevant trouvée pour l'instant.")

# ============================================================
# 7. STATUT DES OFFRES (open/closed)
# ============================================================
print("\n" + "=" * 70)
print("7. STATUT DES OFFRES")
print("=" * 70 + "\n")

status = pd.read_sql("""
    SELECT status, COUNT(*) as nb
    FROM jobs
    GROUP BY status
""", conn)
print(status.to_string(index=False))

conn.close()

print("\n" + "=" * 70)
print("ANALYSE TERMINÉE")
print("=" * 70)