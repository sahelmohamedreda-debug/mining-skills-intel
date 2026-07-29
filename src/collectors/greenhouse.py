import re
import html
import sys
from pathlib import Path

import requests

# Permet d'importer le module db.py qui se trouve dans un autre dossier (src/db/)
sys.path.append(str(Path(__file__).parent.parent))
from db.db import init_db, insert_job, count_jobs

BOARD_TOKEN = "koboldmetals"
COMPANY_NAME = "KoBold Metals"


def fetch_jobs(board_token: str) -> list:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data["jobs"]


def clean_description(html_text: str) -> str:
    text_decoded = html.unescape(html_text)
    text_decoded = html.unescape(text_decoded)
    text_without_tags = re.sub(r"<[^>]+>", " ", text_decoded)
    text_clean = re.sub(r"\s+", " ", text_without_tags).strip()
    return text_clean


if __name__ == "__main__":
    # 1. Prépare la base de données (crée la table si besoin)
    init_db()

    # 2. Appelle l'API pour récupérer les offres brutes
    raw_jobs = fetch_jobs(BOARD_TOKEN)
    print(f"{len(raw_jobs)} offres récupérées depuis l'API Greenhouse\n")

    # 3. Insère chaque offre en base
    nb_inserees = 0
    nb_doublons = 0

    for job in raw_jobs:
        job_data = {
            "external_id": str(job["id"]),
            "company": COMPANY_NAME,
            "title": job["title"],
            "location": job["location"]["name"],
            "description": clean_description(job.get("content", "")),
            "url": job.get("absolute_url", ""),
            "source": "greenhouse",
        }

        was_inserted = insert_job(job_data)
        if was_inserted:
            nb_inserees += 1
        else:
            nb_doublons += 1

    # 4. Résumé + vérification
    print(f"Nouvelles offres insérées : {nb_inserees}")
    print(f"Doublons ignorés          : {nb_doublons}")
    print(f"Total en base maintenant  : {count_jobs()}")