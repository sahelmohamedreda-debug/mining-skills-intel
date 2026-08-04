import requests
import json

response = requests.get("https://api.rippling.com/platform/api/ats/v1/board/lilac-solutions/jobs")
data = response.json()

# Affiche la structure brute du tout premier job, telle quelle
raw_jobs = data if isinstance(data, list) else data.get("jobs", [])
print(json.dumps(raw_jobs[0], indent=2))