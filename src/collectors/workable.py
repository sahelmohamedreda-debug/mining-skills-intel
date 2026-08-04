import requests
from common import clean_description, store_jobs


def fetch_jobs(account_subdomain: str, company_name: str) -> list:
    """Récupère et formate les offres Workable pour une entreprise donnée."""
    url = f"https://apply.workable.com/api/v1/widget/accounts/{account_subdomain}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    raw_jobs = data["jobs"]

    jobs_data = []
    for job in raw_jobs:
        jobs_data.append({
            "external_id": str(job.get("shortcode", job.get("id", ""))),
            "company": company_name,
            "title": job["title"],
            "location": f"{job.get('city', '')}, {job.get('country', '')}".strip(", ") or "Remote",
            "description": clean_description(job.get("description", "")),
            "url": job.get("url", ""),
            "source": "workable",
        })
    return jobs_data


def run(account_subdomain: str, company_name: str) -> None:
    jobs_data = fetch_jobs(account_subdomain, company_name)
    store_jobs(jobs_data, company_name)