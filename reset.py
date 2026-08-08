import sys
sys.path.append('src')
from db.db import get_connection
conn = get_connection()
conn.execute("UPDATE extraction_progress SET last_processed_job_id = 27, total_processed = 27 WHERE id = 1")
conn.commit()
conn.close()
print('Progression remise a ID 27')
