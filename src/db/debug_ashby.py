import requests
import json

response = requests.get("https://api.ashbyhq.com/posting-api/job-board/marianaminerals")
data = response.json()
print(json.dumps(data["jobs"][0], indent=2))