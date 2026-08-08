import subprocess
import time
import sys

sys.path.append('src')
from db.db import get_connection

WAIT_MINUTES = 30
MAX_RUNS = 50

for i in range(1, MAX_RUNS + 1):
    print(f"\n{'='*60}")
    print(f"BATCH AUTO #{i} - {time.strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(["python", "src/extraction/extract_batch.py"])
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM jobs")
    total = c.fetchone()[0]
    c.execute("SELECT last_processed_job_id FROM extraction_progress")
    last = c.fetchone()[0]
    conn.close()
    
    print(f"\nProgression : {last}/{total} offres ({100*last//total if total else 0}%)")
    
    if last >= total:
        print("\nTOUTES LES OFFRES SONT TRAITEES !")
        break
    
    print(f"Prochain batch dans {WAIT_MINUTES} minutes... (Ctrl+C pour arreter)")
    time.sleep(WAIT_MINUTES * 60)
