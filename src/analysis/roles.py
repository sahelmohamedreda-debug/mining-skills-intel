# src/analysis/roles.py
"""
Normalisation des intitulés de poste vers un référentiel de rôles.

Les intitulés bruts varient énormément d'une entreprise à l'autre
(ex: "Staff Electrical Design Engineer, EPC" vs "Electrician" vs
"Substation Protection and Control Engineer") — ce module regroupe
ces variantes sous un petit nombre de rôles canoniques, à l'aide de
règles par mots-clés (pas de LLM, rapide et déterministe).

Logique générale, dans l'ordre de priorité :
  1. RH / Recrutement
  2. Direction / Exécutif
  3. Si le mot "engineer" apparaît (en mot entier) → sous-catégories
     d'ingénierie (électrique, mécanique, procédés, logiciel/data,
     systèmes/contrôles, structure, ou "autre spécialité")
  4. Géologie / Exploration
  5. Technicien / Opérateur
  6. Manager / Chef de projet
  7. Spécialiste / Analyste / Coordinateur
  8. Designer
  9. Autre / Non classé (fallback)

L'ordre compte : par exemple "Lead Maintenance Technician" doit tomber
dans "Technicien / Opérateur" (le mot "technician" est décisif), pas
dans "Manager" à cause du mot "Lead" — donc le bloc Technicien est
vérifié AVANT le bloc Manager.
"""

import re


def _has(word: str, text: str) -> bool:
    """Vérifie la présence d'un mot ou d'une expression en tant que mot entier."""
    return re.search(rf"\b{re.escape(word)}\b", text) is not None


# Règles pour les sous-catégories d'ingénierie (vérifiées seulement si
# "engineer" apparaît comme mot entier dans le titre)
_ENGINEERING_RULES = [
    ("Ingénieur Électrique", ["electrical", "substation", "bess"]),
    ("Ingénieur Mécanique", ["mechanical"]),
    ("Ingénieur Procédés", ["process"]),
    ("Ingénieur Logiciel / Data", ["software", "machine learning", "test automation", "data"]),
    ("Ingénieur Systèmes / Contrôles", ["systems", "controls", "instrumentation", "protection and control"]),
    ("Ingénieur Structure", ["structural"]),
]

_RH_KEYWORDS = ["hr business partner", "hrbp", "recruiter", "human resources", "talent acquisition"]
_DIRECTION_KEYWORDS = ["vice president", "chief", "director", "head of"]
_GEOLOGY_KEYWORDS = ["geolog", "mineral exploration", "geoscien"]
_TECHNICIAN_KEYWORDS = ["technician", "operator", "electrician", "associate"]
_MANAGEMENT_KEYWORDS = ["manager", "supervisor", "superintendent", "lead", "planner"]
_SPECIALIST_KEYWORDS = ["specialist", "analyst", "coordinator"]
_DESIGNER_KEYWORDS = ["designer"]


def normalize_role(title: str) -> str:
    """Renvoie le rôle canonique correspondant à un intitulé de poste brut."""
    if not title or not isinstance(title, str):
        return "Autre / Non classé"

    t = title.lower()

    if any(_has(k, t) for k in _RH_KEYWORDS):
        return "RH / Recrutement"

    if any(_has(k, t) for k in _DIRECTION_KEYWORDS):
        return "Direction / Exécutif"

    if _has("engineer", t):
        for role_name, keywords in _ENGINEERING_RULES:
            if any(_has(k, t) for k in keywords):
                return role_name
        return "Ingénieur (autre spécialité)"

    if any(_has(k, t) for k in _GEOLOGY_KEYWORDS):
        return "Géologie / Exploration"

    if any(_has(k, t) for k in _TECHNICIAN_KEYWORDS):
        return "Technicien / Opérateur"

    if any(_has(k, t) for k in _MANAGEMENT_KEYWORDS):
        return "Manager / Chef de projet"

    if any(_has(k, t) for k in _SPECIALIST_KEYWORDS):
        return "Spécialiste / Analyste"

    if any(_has(k, t) for k in _DESIGNER_KEYWORDS):
        return "Designer"

    return "Autre / Non classé"
