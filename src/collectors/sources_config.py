# src/collectors/config.py
"""
Configuration des entreprises à scraper.

La liste des entreprises n'est plus en dur dans ce fichier : elle vit dans
config/sources.json, éditable via la page admin du dashboard
(src/dashboard/pages/admin.py) sans toucher au code.

Ce module garde SOURCES au même format qu'avant — une liste de tuples
(platform, slug, name) — pour ne rien casser dans le reste du pipeline
(run_all_collectors.py et les collecteurs par plateforme continuent de
fonctionner sans modification).
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "sources.json"


def load_sources() -> list[dict]:
    """Charge la liste complète des sources (actives et désactivées) depuis le JSON."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("sources", [])


def get_active_sources() -> list[tuple[str, str, str]]:
    """
    Renvoie uniquement les sources actives (enabled=true), au format
    (platform, slug, name) attendu par le reste du pipeline de collecte.
    """
    return [
        (s["platform"], s["slug"], s["name"])
        for s in load_sources()
        if s.get("enabled", True)
    ]


# Chargé une fois à l'import, pour compatibilité avec le code existant
# qui fait `from collectors.config import SOURCES`.
# ⚠️ Si tu ajoutes une entreprise via la page admin PENDANT que le pipeline
# tourne déjà, ce process ne la verra qu'au prochain lancement (nouvel import).
SOURCES = get_active_sources()
