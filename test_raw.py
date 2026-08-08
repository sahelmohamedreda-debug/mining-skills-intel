import sys, os, json
from dotenv import load_dotenv
from groq import Groq

sys.path.append('src')
from db.db import get_connection

load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

conn = get_connection()
c = conn.cursor()
c.execute('SELECT id, title, description FROM jobs WHERE id=28')
job = c.fetchone()

prompt = "Tu es expert en competences minieres.\nTitre : " + job[1] + "\nDescription : " + job[2][:1500] + "\n\nRetourne UNIQUEMENT ce JSON:\n{\"skills\": [{\"skill\": \"...\", \"category\": \"...\", \"compliance_relevant\": true/false}], \"out_of_scope\": [\"...\"]}"

response = client.chat.completions.create(
    model='openai/gpt-oss-20b',
    messages=[{'role': 'user', 'content': prompt}],
    temperature=0.3,
    max_tokens=1000,
)

raw = response.choices[0].message.content
print('=== REPONSE BRUTE ===')
print(raw[:1500])
print('=== FIN ===')
conn.close()
