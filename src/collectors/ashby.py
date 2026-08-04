import requests
from common import clean_description, store_jobs


def fetch_jobs(job_board_name: str, company_name: str) -> list:
    """Récupère et formate les offres Ashby pour une entreprise donnée."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{job_board_name}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    raw_jobs = data["jobs"]

    jobs_data = []
    for job in raw_jobs:
        jobs_data.append({
            "external_id": str(job.get("id", "")),
            "company": company_name,
            "title": job["title"],
            "location": job.get("location", "Remote"),
            "description": clean_description(job.get("descriptionHtml", "")),
            "url": job.get("jobUrl", job.get("applyUrl", "")),
            "source": "ashby",
        })
    return jobs_data


def run(job_board_name: str, company_name: str) -> None:
    jobs_data = fetch_jobs(job_board_name, company_name)
    store_jobs(jobs_data, company_name)