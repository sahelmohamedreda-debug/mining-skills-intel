import sys
from pathlib import Path
from difflib import SequenceMatcher

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT id, skill_name, category FROM skills ORDER BY category, skill_name")
all_skills = cursor.fetchall()

print(f"Total compétences en base : {len(all_skills)}\n")
print("=== DOUBLONS POTENTIELS (similarité > 80%) ===\n")

duplicates_found = []
for i, (id1, name1, cat1) in enumerate(all_skills):
    for id2, name2, cat2 in all_skills[i+1:]:
        if cat1 != cat2:
            continue
        similarity = SequenceMatcher(None, name1.lower(), name2.lower()).ratio()
        if similarity > 0.8 and name1.lower() != name2.lower():
            duplicates_found.append((name1, name2, cat1, similarity))

for name1, name2, cat, sim in sorted(duplicates_found, key=lambda x: -x[3]):
    print(f"  '{name1}' <-> '{name2}' ({cat}) — similarité {sim:.0%}")

print(f"\nTotal paires suspectes trouvées : {len(duplicates_found)}")

conn.close()