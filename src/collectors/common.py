import re
import html
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from db.db import insert_job


def clean_description(html_text: str) -> str:
    """Nettoie une description HTML : décodage + retrait des balises."""
    text_decoded = html.unescape(html_text or "")
    text_decoded = html.unescape(text_decoded)
    text_without_tags = re.sub(r"<[^>]+>", " ", text_decoded)
    text_clean = re.sub(r"\s+", " ", text_without_tags).strip()
    return text_clean


def store_jobs(jobs_data: list, source_name: str) -> tuple:
    """
    Prend une liste de dictionnaires déjà au bon format (job_data)
    et les insère en base. Retourne (nb_inserees, nb_doublons).
    """
    nb_inserees = 0
    nb_doublons = 0

    for job_data in jobs_data:
        was_inserted = insert_job(job_data)
        if was_inserted:
            nb_inserees += 1
        else:
            nb_doublons += 1

    print(f"  [{source_name}] Nouvelles offres : {nb_inserees} | Doublons ignorés : {nb_doublons}")
    return nb_inserees, nb_doublons