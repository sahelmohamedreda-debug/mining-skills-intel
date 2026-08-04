import requests
import json

response = requests.get("https://apply.workable.com/api/v1/widget/accounts/americanbatterytechnologycompany")
data = response.json()
print(json.dumps(data["jobs"][0], indent=2))