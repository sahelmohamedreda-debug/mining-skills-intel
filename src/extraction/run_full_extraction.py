"""Lance l'extraction en boucle jusqu'à épuisement ou fin des offres"""
import subprocess
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db.db import get_connection

def get_remaining_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_processed_job_id FROM extraction_progress WHERE id = 1")
    last_id = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE id > ?", (last_id,))
    remaining = cursor.fetchone()[0]
    conn.close()
    return remaining

if __name__ == "__main__":
    max_runs = 30  # Sécurité : max 30 lancements dans cette session
    run_count = 0
    
    while run_count < max_runs:
        remaining = get_remaining_count()
        
        if remaining == 0:
            print("✅ Toutes les offres sont traitées !")
            break
        
        print(f"\n🔄 Lancement #{run_count + 1} | {remaining} offres restantes\n")
        
        result = subprocess.run(
            [sys.executable, "src/extraction/extract_batch.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        # Si rate limit détecté, on attend plus longtemps
        if "RATE LIMIT" in result.stdout or "429" in result.stdout:
            print("⏳ Rate limit détecté — pause de 60 secondes...")
            time.sleep(60)
        else:
            time.sleep(5)  # Petite pause entre les batches
        
        run_count += 1
    
    print(f"\n📊 Session terminée après {run_count} lancements")
    print(f"Offres restantes : {get_remaining_count()}")