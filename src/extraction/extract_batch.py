import json, sys, time, os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
from db.db import get_connection
from extraction.extract_skills import extract_skills_from_description

load_dotenv()
BATCH_SIZE = 10
DELAY = 2.5

def store_skills_for_job(conn, job_id, skills_data):
    cursor = conn.cursor()
    skills_count, out_count = 0, 0
    valid = ["Operational & Technical", "Health, Safety & Risk Management", "Digital & Automation", "Soft & Leadership"]
    for s in skills_data.get("skills", []):
        sn, cat = s["skill"].strip(), s.get("category", "")
        if not sn or cat not in valid: continue
        try:
            cursor.execute("INSERT OR IGNORE INTO skills (skill_name, category, compliance_relevant) VALUES (?, ?, ?)", (sn, cat, s.get("compliance_relevant", False)))
            cursor.execute("SELECT id FROM skills WHERE skill_name = ? AND category = ?", (sn, cat))
            cursor.execute("INSERT OR IGNORE INTO job_skills (job_id, skill_id) VALUES (?, ?)", (job_id, cursor.fetchone()[0]))
            skills_count += 1
        except: pass
    for sn in skills_data.get("out_of_scope", []):
        sn = sn.strip()
        if not sn: continue
        try:
            cursor.execute("INSERT OR IGNORE INTO job_out_of_scope (job_id, skill_name) VALUES (?, ?)", (job_id, sn))
            out_count += 1
        except: pass
    conn.commit()
    return {"skills": skills_count, "out_of_scope": out_count}

def get_progress(conn):
    c = conn.cursor()
    c.execute("SELECT last_processed_job_id FROM extraction_progress WHERE id = 1")
    r = c.fetchone()
    return r[0] if r else 0

def update_progress(conn, job_id):
    conn.cursor().execute("UPDATE extraction_progress SET last_processed_job_id = ?, total_processed = total_processed + 1, last_updated = CURRENT_TIMESTAMP WHERE id = 1", (job_id,))
    conn.commit()

if __name__ == "__main__":
    conn = get_connection()
    last = get_progress(conn)
    c = conn.cursor()
    c.execute("SELECT id, title, description FROM jobs WHERE id > ? ORDER BY id LIMIT ?", (last, BATCH_SIZE))
    offres = c.fetchall()
    if not offres:
        print("Tout fini !")
        conn.close()
        sys.exit(0)
    c.execute("SELECT COUNT(*) FROM jobs WHERE id > ?", (last,))
    print(f"\nBATCH : {len(offres)} offres | Reste : {c.fetchone()[0]} | Depart ID #{last+1}\n")
    
    for i, (job_id, title, desc) in enumerate(offres, 1):
        print(f"[{i}/{len(offres)}] #{job_id} : {title[:50]}...", end=" ", flush=True)
        try:
            data = extract_skills_from_description(title, desc)
            err = str(data.get("error", ""))
            
            # RATE LIMIT = on arrete TOUT, on n'avance PAS
            if "429" in err or "rate_limit" in err.lower():
                print("RATE LIMIT - arret")
                conn.commit()
                conn.close()
                print(f"\nReprendra a ID #{job_id}")
                sys.exit(0)
            
            if "error" in data:
                print(f"X {err[:40]}")
                update_progress(conn, job_id)
                continue
            
            counts = store_skills_for_job(conn, job_id, data)
            update_progress(conn, job_id)
            print(f"OK {counts['skills']}s {counts['out_of_scope']}o")
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower():
                print("RATE LIMIT - arret")
                conn.commit()
                conn.close()
                print(f"\nReprendra a ID #{job_id}")
                sys.exit(0)
            print(f"X {err[:40]}")
            update_progress(conn, job_id)
        time.sleep(DELAY)
    conn.close()
    print(f"\nFini - Dernier ID : {offres[-1][0]}")
