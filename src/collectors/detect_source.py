# src/collectors/detect_source.py
"""
Détection automatique de la plateforme ATS et du slug d'une entreprise à
partir d'une simple URL (site web ou page carrière).

Principe :
  1. On télécharge le HTML brut de la page fournie.
  2. On cherche des motifs d'URL connus des 4 plateformes déjà supportées
     (Greenhouse, Workable, Ashby, Rippling).
  3. Si un candidat est trouvé, on VALIDE en appelant réellement l'API de
     la plateforme (les mêmes endpoints que les collecteurs existants) —
     un motif trouvé dans le HTML ne suffit pas, il faut confirmer que les
     offres sont vraiment accessibles.

Limite connue et assumée : si la page carrière charge son contenu en
JavaScript (React, Vue...) plutôt que d'inclure un lien brut vers l'ATS
dans le HTML initial, ce script ne trouvera rien — un `requests.get`
simple ne voit que le HTML tel que livré par le serveur, pas ce qui est
injecté ensuite par le navigateur. Dans ce cas, il faut chercher le lien
manuellement (comme pour les 5 entreprises initiales du projet).
"""

import re
import sys
import requests

TIMEOUT = 10

# (nom_plateforme, regex_pour_extraire_le_slug)
# L'ordre compte peu ici car les domaines ne se chevauchent pas.
PATTERNS = [
    ("greenhouse", re.compile(r"(?:boards|job-boards)\.greenhouse\.io/(?:embed/job_board\?for=)?([a-zA-Z0-9_-]+)")),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_-]+)")),
    ("workable", re.compile(r"apply\.workable\.com/([a-zA-Z0-9_-]+)")),
    ("workable", re.compile(r"([a-zA-Z0-9-]+)\.workable\.com")),
    ("rippling", re.compile(r"ats\.rippling\.com/([a-zA-Z0-9_-]+)/jobs")),
    ("rippling", re.compile(r"([a-zA-Z0-9-]+)\.rippling-ats\.com")),
]


def find_candidates(url: str) -> list[tuple[str, str]]:
    """Cherche dans le HTML brut de `url` des motifs correspondant aux 4 plateformes.
    Renvoie une liste de (platform, slug) candidats, potentiellement vide."""
    try:
        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Impossible de charger {url} : {e}")

    html = response.text
    candidates = []
    for platform, pattern in PATTERNS:
        for match in pattern.finditer(html):
            slug = match.group(1)
            if platform == "workable" and slug.lower() == "apply":
                continue  # faux positif : "apply.workable.com" n'est pas un slug d'entreprise
            if (platform, slug) not in candidates:
                candidates.append((platform, slug))
    return candidates


def validate_candidate(platform: str, slug: str) -> tuple[bool, str]:
    """
    Vérifie que le slug fonctionne vraiment en appelant l'API réelle de la
    plateforme (mêmes endpoints que les collecteurs). Renvoie (ok, message).
    """
    try:
        if platform == "greenhouse":
            r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs", timeout=TIMEOUT)
            r.raise_for_status()
            n = len(r.json().get("jobs", []))
        elif platform == "ashby":
            r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=TIMEOUT)
            r.raise_for_status()
            n = len(r.json().get("jobs", []))
        elif platform == "workable":
            r = requests.get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}", timeout=TIMEOUT)
            r.raise_for_status()
            n = len(r.json().get("jobs", []))
        elif platform == "rippling":
            r = requests.get(f"https://api.rippling.com/platform/api/ats/v1/board/{slug}/jobs", timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
            n = len(data if isinstance(data, list) else data.get("jobs", []))
        else:
            return False, f"Plateforme inconnue : {platform}"
    except requests.exceptions.RequestException as e:
        return False, f"Échec de validation ({e})"

    return True, f"{n} offre(s) trouvée(s) via l'API {platform}"


def detect_source(url: str) -> dict | None:
    """
    Fonction principale : renvoie le premier candidat VALIDÉ sous la forme
    {"platform": ..., "slug": ..., "message": ...}, ou None si rien n'a pu
    être détecté ni validé.
    """
    candidates = find_candidates(url)
    for platform, slug in candidates:
        ok, message = validate_candidate(platform, slug)
        if ok:
            return {"platform": platform, "slug": slug, "message": message}
    return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python detect_source.py <url_entreprise>")
        sys.exit(1)

    target_url = sys.argv[1]
    print(f"Recherche d'un lien ATS dans {target_url} ...")
    result = detect_source(target_url)
    if result:
        print(f"✅ Détecté : platform={result['platform']}, slug={result['slug']}")
        print(f"   {result['message']}")
    else:
        print("❌ Aucune plateforme supportée détectée (ou lien chargé en JavaScript, invisible ici).")
        print("   → Cherche manuellement le lien vers la page carrière dans le site.")