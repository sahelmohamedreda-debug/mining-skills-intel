# src/analysis/analyze_roles.py
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from db.db import get_connection
from analysis.roles import normalize_role

conn = get_connection()

jobs = pd.read_sql("SELECT id, title, company FROM jobs", conn)
skills = pd.read_sql("""
    SELECT js.job_id, s.skill_name, s.category
    FROM job_skills js
    JOIN skills s ON js.skill_id = s.id
""", conn)
conn.close()

jobs["role"] = jobs["title"].apply(normalize_role)

print("=" * 70)
print("1. DISTRIBUTION DES RÔLES NORMALISÉS")
print("=" * 70 + "\n")

role_counts = jobs["role"].value_counts().reset_index()
role_counts.columns = ["role", "nb_offres"]
print(role_counts.to_string(index=False))

print("\n" + "=" * 70)
print("2. TITRES TOMBÉS DANS « Autre / Non classé » (à vérifier)")
print("=" * 70 + "\n")

unclassified = jobs[jobs["role"] == "Autre / Non classé"][["title", "company"]].drop_duplicates()
if len(unclassified) > 0:
    print(unclassified.to_string(index=False))
else:
    print("Aucun titre non classé. 🎉")

print("\n" + "=" * 70)
print("3. TOP 8 COMPÉTENCES PAR RÔLE (rôles avec au moins 3 offres)")
print("=" * 70)

merged = skills.merge(jobs[["id", "role"]], left_on="job_id", right_on="id")

for role in role_counts[role_counts["nb_offres"] >= 3]["role"]:
    role_skills = merged[merged["role"] == role]
    top = (
        role_skills.groupby("skill_name")
        .size()
        .reset_index(name="nb")
        .sort_values("nb", ascending=False)
        .head(8)
    )
    n_jobs_role = jobs[jobs["role"] == role].shape[0]
    print(f"\n--- {role} ({n_jobs_role} offres) ---")
    if len(top) > 0:
        print(top.to_string(index=False))
    else:
        print("(aucune compétence extraite pour ce rôle)")

print("\n" + "=" * 70)
print("ANALYSE TERMINÉE")
print("=" * 70)
