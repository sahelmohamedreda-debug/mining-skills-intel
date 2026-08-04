import requests
from common import clean_description, store_jobs


def fetch_jobs(board_slug: str, company_name: str) -> list:
    """Récupère et formate les offres Rippling pour une entreprise donnée."""
    url = f"https://api.rippling.com/platform/api/ats/v1/board/{board_slug}/jobs"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    # Rippling peut renvoyer soit une liste directe, soit un objet avec une clé "jobs"
    raw_jobs = data if isinstance(data, list) else data.get("jobs", [])

    jobs_data = []
    for job in raw_jobs:
        jobs_data.append({
            "external_id": str(job.get("uuid", job.get("id", ""))),
            "company": company_name,
            "title": job.get("name", job.get("title", "")),
            "location": job.get("workLocation", {}).get("label", "Remote") if isinstance(job.get("workLocation"), dict) else "Remote",
            "description": clean_description(job.get("description", "")),
            "url": job.get("url", ""),
            "source": "rippling",
        })
    return jobs_data


def run(board_slug: str, company_name: str) -> None:
    jobs_data = fetch_jobs(board_slug, company_name)
    store_jobs(jobs_data, company_name)