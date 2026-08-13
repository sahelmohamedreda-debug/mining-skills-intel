"""
Fusionne les compétences qui ne diffèrent que par la casse
(ex: 'Project Management' / 'project management' / 'Project management')
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.db"

def normalize_casing():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, skill_name, category FROM skills")
    all_skills = cursor.fetchall()

    # Groupe par (nom en minuscules, catégorie) -> liste des vrais id
    groups = {}
    for skill_id, name, category in all_skills:
        key = (name.lower().strip(), category)
        groups.setdefault(key, []).append((skill_id, name))

    merged_count = 0
    for (name_lower, category), entries in groups.items():
        if len(entries) <= 1:
            continue  # Pas de doublon pour cette compétence

        # Garde le premier comme "référence", fusionne les autres dedans
        reference_id, reference_name = entries[0]
        for duplicate_id, duplicate_name in entries[1:]:
            # Redirige tous les liens job_skills vers la référence
            cursor.execute(
                "UPDATE OR IGNORE job_skills SET skill_id = ? WHERE skill_id = ?",
                (reference_id, duplicate_id)
            )
            # Supprime les liens devenus doublons après redirection
            cursor.execute(
                "DELETE FROM job_skills WHERE skill_id = ?", (duplicate_id,)
            )
            # Supprime la compétence doublon elle-même
            cursor.execute("DELETE FROM skills WHERE id = ?", (duplicate_id,))
            merged_count += 1

    conn.commit()
    print(f"✅ {merged_count} doublons de casse fusionnés")
    conn.close()

if __name__ == "__main__":
    normalize_casing()