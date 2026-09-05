# src/dashboard/pages/admin.py
"""
Page admin — gestion des entreprises suivies par le pipeline.

Permet d'ajouter, modifier, activer/désactiver ou supprimer une entreprise
sans toucher au code. Les changements sont écrits dans config/sources.json,
lu par src/collectors/config.py au prochain lancement du pipeline.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent.parent))
from collectors.detect_source import find_candidates, validate_candidate

st.set_page_config(page_title="Admin — Entreprises", page_icon="🛠️", layout="wide")

CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "sources.json"

PLATFORMS = ["greenhouse", "workable", "ashby", "rippling"]

# ============================================================
# PROTECTION PAR MOT DE PASSE
# ============================================================
def check_password() -> bool:
    """
    Affiche un écran de mot de passe et renvoie True seulement si le bon
    mot de passe a été saisi. Le mot de passe attendu vient de
    .streamlit/secrets.toml (jamais commité sur GitHub — voir .gitignore),
    sous la clé [admin] password = "...".
    """
    if st.session_state.get("admin_authenticated", False):
        return True

    st.markdown("## 🔒 Page protégée")

    if "admin" not in st.secrets or "password" not in st.secrets.get("admin", {}):
        st.error(
            "Aucun mot de passe n'est configuré. Crée un fichier "
            "`.streamlit/secrets.toml` avec :\n\n"
            "```toml\n[admin]\npassword = \"ton_mot_de_passe\"\n```"
        )
        st.stop()

    pwd = st.text_input("Mot de passe admin", type="password")

    if pwd:
        if pwd == st.secrets["admin"]["password"]:
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect.")

    st.stop()


check_password()


def load_sources() -> list[dict]:
    if not CONFIG_PATH.exists():
        return []
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f).get("sources", [])


def save_sources(sources: list[dict]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"sources": sources}, f, ensure_ascii=False, indent=2)


st.markdown("## 🛠️ Administration — Entreprises suivies")

if st.sidebar.button("🔓 Se déconnecter"):
    st.session_state["admin_authenticated"] = False
    st.rerun()

st.markdown(
    "Ajoute, modifie ou désactive une entreprise ici. Le pipeline de collecte "
    "lira ces changements **au prochain lancement** (pas en temps réel)."
)

st.info(
    "ℹ️ **Où trouver `platform` et `slug`** : ce sont les mêmes valeurs que "
    "celles utilisées dans l'URL de l'API publique de l'ATS de l'entreprise "
    "(Greenhouse, Workable, Ashby, Rippling). Vérifie toujours que l'accès "
    "est autorisé (robots.txt, conditions d'utilisation) avant d'ajouter une "
    "nouvelle source, comme documenté dans le rapport de stage."
)

sources = load_sources()
df = pd.DataFrame(sources)

if df.empty:
    df = pd.DataFrame(columns=["id", "name", "platform", "slug", "sector", "enabled"])

# S'assurer que toutes les colonnes attendues existent, même sur un JSON partiel
for col, default in [("id", ""), ("name", ""), ("platform", PLATFORMS[0]),
                      ("slug", ""), ("sector", ""), ("enabled", True)]:
    if col not in df.columns:
        df[col] = default

df = df[["enabled", "name", "platform", "slug", "sector", "id"]]

st.markdown("### 🔎 Ajouter automatiquement depuis une URL")
st.caption(
    "Cherche un lien vers une plateforme ATS connue (Greenhouse, Workable, Ashby, Rippling) "
    "dans le HTML de la page fournie, puis vérifie que les offres sont bien accessibles. "
    "⚠️ Ne fonctionne pas si la page carrière charge son contenu en JavaScript — dans ce "
    "cas, ajoute l'entreprise manuellement dans le tableau ci-dessous."
)

col_url, col_name, col_btn = st.columns([3, 2, 1])
with col_url:
    detect_url = st.text_input("URL du site ou de la page carrière", placeholder="https://www.exemple.com/careers")
with col_name:
    detect_company_name = st.text_input("Nom à afficher", placeholder="Nom de l'entreprise")
with col_btn:
    st.markdown("&nbsp;")
    run_detection = st.button("🔍 Détecter", use_container_width=True)

if run_detection:
    if not detect_url.strip():
        st.warning("Renseigne une URL d'abord.")
    else:
        with st.spinner("Recherche et validation en cours..."):
            try:
                candidates = find_candidates(detect_url.strip())
                result = None
                for platform, slug in candidates:
                    ok, message = validate_candidate(platform, slug)
                    if ok:
                        result = {"platform": platform, "slug": slug, "message": message}
                        break
            except RuntimeError as e:
                st.error(f"❌ {e}")
                result = None
                candidates = []

        if result:
            st.success(f"✅ Détecté : **{result['platform']}** / slug `{result['slug']}` — {result['message']}")
            st.session_state["detected_source"] = {
                "platform": result["platform"],
                "slug": result["slug"],
                "name": detect_company_name.strip() or result["slug"],
            }
        elif candidates:
            st.warning(
                f"Des liens ont été trouvés ({candidates}) mais aucun n'a pu être validé "
                "via l'API réelle — le slug est peut-être incorrect ou le board est privé."
            )
        else:
            st.info(
                "Aucune plateforme supportée détectée dans le HTML de cette page. "
                "Le lien est peut-être chargé en JavaScript — ajoute l'entreprise manuellement."
            )

if "detected_source" in st.session_state:
    d = st.session_state["detected_source"]
    st.markdown(f"**Prêt à ajouter :** {d['name']} — {d['platform']} / `{d['slug']}`")
    col_add, col_cancel = st.columns([1, 1])
    with col_add:
        if st.button("➕ Ajouter cette entreprise", type="primary"):
            sources = load_sources()
            new_id = re.sub(r"[^a-z0-9]", "", d["name"].lower()) or d["slug"]
            sources.append({
                "id": new_id,
                "name": d["name"],
                "platform": d["platform"],
                "slug": d["slug"],
                "sector": "",
                "enabled": True,
            })
            save_sources(sources)
            del st.session_state["detected_source"]
            st.success(f"✅ {d['name']} ajoutée à config/sources.json.")
            st.rerun()
    with col_cancel:
        if st.button("Annuler"):
            del st.session_state["detected_source"]
            st.rerun()

st.markdown("---")
st.markdown("### Liste des entreprises")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    column_config={
        "enabled": st.column_config.CheckboxColumn("Actif", help="Décoche pour suspendre la collecte sans supprimer l'entrée"),
        "name": st.column_config.TextColumn("Nom affiché", required=True),
        "platform": st.column_config.SelectboxColumn("Plateforme", options=PLATFORMS, required=True),
        "slug": st.column_config.TextColumn("Slug (identifiant ATS)", required=True,
                                             help="Ex: 'redwoodmaterials' — visible dans l'URL de l'API de la plateforme"),
        "sector": st.column_config.TextColumn("Secteur", help="Ex: 'Recyclage de batteries', 'Phosphate'..."),
        "id": st.column_config.TextColumn("id interne", required=True,
                                           help="Identifiant unique, sans espace (ex: 'redwoodmaterials')"),
    },
    key="sources_editor",
)

col_save, col_reload, _ = st.columns([1, 1, 3])

with col_save:
    if st.button("💾 Sauvegarder", type="primary", use_container_width=True):
        errors = []

        cleaned = edited_df.copy()
        cleaned["name"] = cleaned["name"].astype(str).str.strip()
        cleaned["slug"] = cleaned["slug"].astype(str).str.strip()
        cleaned["id"] = cleaned["id"].astype(str).str.strip()

        if cleaned["name"].eq("").any() or cleaned["slug"].eq("").any() or cleaned["id"].eq("").any():
            errors.append("Chaque ligne doit avoir un nom, un slug et un id non vides.")

        if cleaned["id"].duplicated().any():
            errors.append("Des id sont dupliqués — chaque entreprise doit avoir un id unique.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            new_sources = cleaned.to_dict(orient="records")
            save_sources(new_sources)
            st.success(f"✅ {len(new_sources)} entreprise(s) sauvegardée(s) dans config/sources.json.")
            st.rerun()

with col_reload:
    if st.button("🔄 Recharger depuis le fichier", use_container_width=True):
        st.rerun()

st.caption(f"Fichier : `{CONFIG_PATH}` — dernière lecture : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

active_count = int(edited_df["enabled"].sum()) if "enabled" in edited_df.columns else 0
st.markdown(f"**{active_count}** entreprise(s) active(s) sur **{len(edited_df)}** au total.")