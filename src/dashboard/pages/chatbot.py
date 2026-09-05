# src/dashboard/pages/chatbot.py
"""
Assistant conversationnel — répond aux questions sur les données déjà
collectées (jamais de connaissance générale, jamais d'invention).

Principe de sécurité et de fiabilité :
  1. Le LLM traduit la question en UNE requête SQL SELECT (JSON strict).
  2. La requête est validée (SELECT uniquement, une seule instruction,
     pas de mots-clés dangereux) avant d'être exécutée.
  3. Exécution sur une connexion SQLite en LECTURE SEULE.
  4. Le résultat affiché est la table réelle renvoyée par la requête —
     pas de résumé généré par un second appel LLM, pour limiter le
     nombre d'appels API (le run initial du projet avait déjà eu des
     problèmes de limite de débit avec Groq).

En cas d'erreur API (limite de débit, timeout...), on affiche un message
clair et un bouton "Réessayer" plutôt qu'un retry automatique en boucle,
qui aggraverait justement le problème de rate-limit.
"""

import json
import re
import sqlite3
from pathlib import Path

import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assistant — Mining Skills", page_icon="💬", layout="wide")

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "jobs.db"

GROQ_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"]  # repli si le premier est indisponible
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Schéma décrit au LLM — à ajuster si ton schéma réel diffère légèrement
SCHEMA_DESCRIPTION = """
Tables disponibles (SQLite) :

jobs(id, external_id, company, title, location, description, url, source, status, date_scraped)
  - status vaut 'open' ou 'closed'

skills(id, skill_name, category, compliance_relevant)
  - category vaut : 'Operational & Technical', 'Health, Safety & Risk Management',
    'Digital & Automation', ou 'Soft & Leadership'
  - compliance_relevant vaut 0 ou 1

job_skills(id, job_id, skill_id)
  - table de liaison entre jobs et skills
"""

SYSTEM_PROMPT = f"""Tu es un générateur de requêtes SQL SQLite en lecture seule.

{SCHEMA_DESCRIPTION}

Règles strictes :
- Réponds UNIQUEMENT avec un objet JSON, rien d'autre, sans balises markdown : {{"sql": "SELECT ..."}}
- La requête doit être un SELECT unique, jamais INSERT/UPDATE/DELETE/DROP/ALTER/ATTACH/PRAGMA.
- Ajoute toujours une clause LIMIT (50 maximum) sauf si la question demande explicitement un total agrégé (COUNT, SUM, AVG...).
- Si la question ne peut pas être répondue avec ces tables, réponds {{"sql": null}}.
"""

FORBIDDEN_KEYWORDS = ["insert", "update", "delete", "drop", "alter", "attach",
                      "pragma", "create", "replace", "vacuum", ";"]


def get_api_key() -> str | None:
    return st.secrets.get("groq", {}).get("api_key")


def _call_groq(model: str, question: str, api_key: str) -> tuple[str | None, str | None, bool]:
    """Renvoie (content, error_message, should_try_next_model)."""
    try:
        response = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0,
                "max_tokens": 300,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
            },
            timeout=20,
        )
    except requests.exceptions.Timeout:
        return None, "⏱️ L'API a mis trop de temps à répondre. Réessaie dans quelques instants.", False
    except requests.exceptions.RequestException as e:
        return None, f"🔌 Impossible de contacter l'API Groq ({e}).", False

    if response.status_code == 404:
        # Modèle indisponible/décommissionné : on tente le suivant dans la liste
        return None, f"Modèle {model} indisponible.", True
    if response.status_code == 429:
        return None, "🚦 Limite de débit atteinte sur Groq (tier gratuit). Attends quelques secondes et réessaie.", False
    if response.status_code == 401:
        return None, "🔑 Clé API Groq invalide ou manquante — vérifie `.streamlit/secrets.toml`.", False
    if response.status_code != 200:
        return None, f"❌ Erreur API Groq (code {response.status_code}) : {response.text[:200]}", False

    return response.json()["choices"][0]["message"]["content"].strip(), None, False


def ask_llm_for_sql(question: str, api_key: str) -> tuple[str | None, str | None]:
    """Renvoie (sql, error_message). Essaie chaque modèle de GROQ_MODELS jusqu'à succès."""
    content = None
    error = None
    for model in GROQ_MODELS:
        content, error, try_next = _call_groq(model, question, api_key)
        if content is not None:
            break
        if not try_next:
            return None, error  # erreur définitive (rate limit, clé invalide, timeout...) : inutile d'essayer un autre modèle

    if content is None:
        return None, error or "Aucun modèle Groq disponible actuellement."

    try:
        content = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return None, "🤖 Réponse du LLM illisible (pas du JSON valide). Reformule ta question."

    sql = parsed.get("sql")
    if not sql:
        return None, "🤷 Cette question ne peut pas être répondue à partir des données disponibles."

    return sql, None


def validate_sql(sql: str) -> str | None:
    """Renvoie un message d'erreur si la requête est jugée dangereuse, sinon None."""
    lowered = sql.strip().lower()
    if not lowered.startswith("select"):
        return "⛔ Requête refusée : seules les requêtes SELECT sont autorisées."
    for kw in FORBIDDEN_KEYWORDS:
        if kw in lowered:
            return f"⛔ Requête refusée : mot-clé interdit détecté (« {kw} »)."
    return None


def run_readonly_query(sql: str) -> tuple[pd.DataFrame | None, str | None]:
    try:
        uri = f"file:{DB_PATH}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        df = pd.read_sql(sql, conn)
        conn.close()
        return df, None
    except sqlite3.Error as e:
        return None, f"❌ Erreur SQL : {e}"


# ============================================================
# INTERFACE
# ============================================================
st.markdown("## 💬 Assistant — Interroge les données")
st.caption(
    "Répond uniquement à partir des données déjà collectées dans la base "
    "(pas de connaissance générale, pas d'invention)."
)

api_key = get_api_key()
if not api_key:
    st.error(
        "Aucune clé API Groq configurée. Ajoute-la dans `.streamlit/secrets.toml` :\n\n"
        "```toml\n[groq]\napi_key = \"ta_cle_groq\"\n```"
    )
    st.stop()

with st.expander("💡 Exemples de questions"):
    st.markdown(
        "- Combien d'offres sont actuellement ouvertes ?\n"
        "- Quelles sont les 5 compétences les plus demandées chez Redwood Materials ?\n"
        "- Combien d'offres viennent de KoBold Metals ?\n"
        "- Quelles compétences sont liées à la conformité réglementaire ?"
    )

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and isinstance(msg["content"], pd.DataFrame):
            st.dataframe(msg["content"], use_container_width=True)
        else:
            st.write(msg["content"])

question = st.chat_input("Pose ta question sur les données collectées...")

if question:
    st.session_state.chat_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Traduction en requête + exécution..."):
            sql, error = ask_llm_for_sql(question, api_key)

        if error:
            st.warning(error)
            st.session_state.chat_history.append({"role": "assistant", "content": error})
        else:
            validation_error = validate_sql(sql)
            if validation_error:
                st.error(validation_error)
                st.session_state.chat_history.append({"role": "assistant", "content": validation_error})
            else:
                st.caption(f"Requête générée : `{sql}`")
                df, exec_error = run_readonly_query(sql)
                if exec_error:
                    st.error(exec_error)
                    st.session_state.chat_history.append({"role": "assistant", "content": exec_error})
                elif df.empty:
                    st.info("Aucun résultat trouvé pour cette question.")
                    st.session_state.chat_history.append({"role": "assistant", "content": "Aucun résultat trouvé."})
                else:
                    st.dataframe(df, use_container_width=True)
                    st.session_state.chat_history.append({"role": "assistant", "content": df})

if st.session_state.chat_history:
    if st.button("🗑️ Effacer la conversation"):
        st.session_state.chat_history = []
        st.rerun()