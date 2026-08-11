"""Test : simule une offre qui disparaît et vérifie qu'elle passe bien à 'closed'"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db import get_connection

conn = get_connection()
cursor = conn.cursor()

# 1. Prend une offre existante et triche : on recule sa last_seen_date de 48h (simule "pas revue depuis 2 jours")
cursor.execute("SELECT id, title FROM jobs LIMIT 1")
test_job_id, test_title = cursor.fetchone()

print(f"=== TEST sur l'offre #{test_job_id} : {test_title} ===\n")

cursor.execute("""
    UPDATE jobs SET last_seen_date = datetime('now', '-48 hours'), status = 'open'
    WHERE id = ?
""", (test_job_id,))
conn.commit()

print("1. Offre simulée comme 'non revue depuis 48h' (statut forcé à open)")

cursor.execute("SELECT status, last_seen_date FROM jobs WHERE id = ?", (test_job_id,))
status_before, last_seen_before = cursor.fetchone()
print(f"   Statut avant : {status_before} | last_seen : {last_seen_before}")

conn.close()

# 2. Lance la logique de fermeture
print("\n2. Exécution de mark_closed_jobs()...")
from collectors.mark_closed_jobs import mark_closed_jobs
mark_closed_jobs()

# 3. Vérifie le résultat
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT status FROM jobs WHERE id = ?", (test_job_id,))
status_after = cursor.fetchone()[0]
conn.close()

print(f"\n3. RÉSULTAT : statut de l'offre #{test_job_id} = '{status_after}'")
if status_after == "closed":
    print("✅ TEST RÉUSSI : l'offre est bien passée à 'closed'")
else:
    print("❌ TEST ÉCHOUÉ : l'offre n'a pas changé de statut")