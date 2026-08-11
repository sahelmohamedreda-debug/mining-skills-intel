import sys, os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPINFRA_API_KEY"),
    base_url="https://api.deepinfra.com/v1/openai",
)

try:
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages=[{"role": "user", "content": "Say hello in one short sentence."}],
        max_tokens=50,
    )
    print("SUCCESS:", response.choices[0].message.content)
except Exception as e:
    print("ERROR:", str(e))