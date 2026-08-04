import requests
from common import clean_description, store_jobs


def fetch_jobs(board_token: str, company_name: str) -> list:
    """Récupère et formate les offres Greenhouse pour une entreprise donnée."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    raw_jobs = data["jobs"]

    jobs_data = []
    for job in raw_jobs:
        jobs_data.append({
            "external_id": str(job["id"]),
            "company": company_name,
            "title": job["title"],
            "location": job["location"]["name"],
            "description": clean_description(job.get("content", "")),
            "url": job.get("absolute_url", ""),
            "source": "greenhouse",
        })
    return jobs_data


def run(board_token: str, company_name: str) -> None:
    jobs_data = fetch_jobs(board_token, company_name)
    store_jobs(jobs_data, company_name)