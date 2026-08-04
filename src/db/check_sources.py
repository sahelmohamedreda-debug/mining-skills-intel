import sqlite3

conn = sqlite3.connect("data/jobs.db")
cursor = conn.execute("""
    SELECT source, company, title, location
    FROM jobs
    WHERE source = 'workable'
    LIMIT 10
""")

for row in cursor.fetchall():
    source, company, title, location = row
    print(f"[{source}] {title} | Lieu : {location}")

conn.close()