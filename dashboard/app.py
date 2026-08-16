# src/dashboard/app.py

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv
from groq import Groq

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="Compétences minières — Tableau de bord",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = Path(__file__).parent.parent / "data" / "jobs.db"
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)

# Initialisation Groq
groq_client = None
if os.getenv("GROQ_API_KEY"):
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ============================================================
# STYLE PERSONNALISÉ MODERNE
# ============================================================
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fb;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1A3A5C, #2C5F8A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #5A7188;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    .metric-card {
        background: white;
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(26, 58, 92, 0.08);
        border: 1px solid rgba(26, 58, 92, 0.06);
        text-align: center;
        flex: 1;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(26, 58, 92, 0.12);
    }
    
    .metric-card .value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1A3A5C;
    }
    
    .metric-card .label {
        font-size: 0.85rem;
        color: #7A8FA0;
        font-weight: 500;
    }
    
    .metric-card .delta {
        font-size: 0.8rem;
        color: #2C6E49;
        background: #E8F5E9;
        padding: 0.1rem 0.6rem;
        border-radius: 12px;
        display: inline-block;
        margin-top: 0.3rem;
    }
    
    .stExpander {
        border: 1px solid rgba(26, 58, 92, 0.1) !important;
        border-radius: 12px !important;
        background: white;
    }
    
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1A3A5C, #2C5F8A) !important;
        color: white !important;
    }
    
    .chat-message-ai {
        background: linear-gradient(135deg, #f0f4f8, #e8edf3);
        padding: 1.2rem;
        border-radius: 14px;
        border-left: 5px solid #2C5F8A;
        margin: 0.8rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #8A9DAE;
        font-size: 0.8rem;
        border-top: 1px solid rgba(26, 58, 92, 0.06);
        margin-top: 2rem;
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, transparent, rgba(26, 58, 92, 0.1), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONNEXION À LA BASE
# ============================================================
@st.cache_data(ttl=3600)  # Rafraîchit toutes les heures
def load_data():
    conn = sqlite3.connect(DB_PATH)

    jobs = pd.read_sql("""
        SELECT id, company, title, location, status, source, date_scraped
        FROM jobs
        WHERE status = 'open'
    """, conn)

    skills = pd.read_sql("""
        SELECT js.job_id, s.skill_name, s.category, s.compliance_relevant,
               j.company, j.location, j.title
        FROM job_skills js
        JOIN skills s ON js.skill_id = s.id
        JOIN jobs j ON js.job_id = j.id
        WHERE j.status = 'open'
    """, conn)

    conn.close()
    return jobs, skills

jobs_df, skills_df = load_data()

if jobs_df.empty:
    st.error("⚠️ Aucune donnée disponible. Vérifie que la base de données contient des offres.")
    st.stop()

# ============================================================
# FONCTION IA GROQ
# ============================================================
def query_groq(question: str, skills_data: pd.DataFrame, jobs_data: pd.DataFrame) -> str:
    if groq_client is None:
        return "⚠️ Clé API Groq non configurée."
    
    if len(skills_data) == 0:
        return "Aucune donnée disponible avec les filtres actuels."

    top_skills = (
        skills_data.groupby(["skill_name", "category"])
        .size()
        .reset_index(name="nb")
        .sort_values("nb", ascending=False)
        .head(20)
    )
    top_skills_text = "\n".join(
        f"- {row['skill_name']} ({row['category']}) : {row['nb']} offres"
        for _, row in top_skills.iterrows()
    )

    by_company = (
        jobs_data.groupby("company").size().reset_index(name="nb")
        .sort_values("nb", ascending=False)
    )
    by_company_text = "\n".join(
        f"- {row['company']} : {row['nb']} offres" for _, row in by_company.iterrows()
    )

    context = f"""Résumé des données filtrées :

TOP 20 COMPÉTENCES :
{top_skills_text}

OFFRES PAR ENTREPRISE :
{by_company_text}

Total : {len(jobs_data)} offres, {len(skills_data)} occurrences"""

    prompt = f"""{context}

Question : {question}

Réponds en français, 3-5 phrases, UNIQUEMENT sur ces données.
Ne jamais utiliser "skills gap"."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erreur: {e}"

# ============================================================
# EN-TÊTE
# ============================================================
st.markdown('<p class="main-header">⛏️ Compétences demandées — Secteur Minier</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyse des compétences dans les offres d\'emploi collectées</p>', unsafe_allow_html=True)

# ⚠️ AVERTISSEMENT VISIBLE (amélioration)
st.warning("""
⚠️ **Important** : ces chiffres montrent ce que les employeurs **demandent** 
dans leurs offres — pas les compétences que possèdent réellement les travailleurs. 
Ce n'est donc PAS un écart offre/demande (« skills gap »), juste une photo de la demande exprimée.
""")

with st.expander("ℹ️ À propos de ces données"):
    st.markdown("""
    **Ce que montrent ces données :** les compétences mentionnées dans les offres d'emploi
    collectées auprès de 5 entreprises du secteur minier.
    
    **Ce qu'elles ne montrent PAS :** les compétences réellement disponibles chez les candidats.
    Il ne s'agit donc pas d'un véritable "skills gap", mais uniquement de la **demande exprimée**.
    
    **Limites :** échantillon limité, extraction par LLM pouvant comporter des imprécisions.
    """)

# ============================================================
# BARRE LATÉRALE — FILTRES
# ============================================================
st.sidebar.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <span style="font-size: 2rem;">⛏️</span>
        <h2 style="color: #1A3A5C; margin: 0; font-size: 1.2rem;">Mining Skills</h2>
        <p style="color: #7A8FA0; font-size: 0.8rem; margin: 0;">Tableau de bord</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# 🔄 Bouton de rafraîchissement (amélioration)
if st.sidebar.button("🔄 Rafraîchir les données", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("### 🔍 Filtres")

companies = ["Toutes"] + sorted(jobs_df["company"].unique().tolist())
selected_company = st.sidebar.selectbox("🏢 Entreprise", companies)

locations = ["Toutes"] + sorted(jobs_df["location"].dropna().unique().tolist())
selected_location = st.sidebar.selectbox("📍 Localisation", locations)

categories = ["Toutes"] + sorted(skills_df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("📂 Catégorie", categories)

# 🔒 Renommer "Compliance" en français (amélioration)
compliance_options = ["Toutes", "Uniquement avec certification", "Uniquement générales"]
selected_compliance = st.sidebar.selectbox("🔒 Type de compétence", compliance_options)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
    <div style="background: #f0f4f8; padding: 0.8rem; border-radius: 10px; text-align: center;">
        <p style="margin: 0; font-size: 0.8rem; color: #5A7188;">
            📊 <b>{len(jobs_df)}</b> offres totales
        </p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# APPLICATION DES FILTRES
# ============================================================
filtered_jobs = jobs_df.copy()
filtered_skills = skills_df.copy()

if selected_company != "Toutes":
    filtered_jobs = filtered_jobs[filtered_jobs["company"] == selected_company]
    filtered_skills = filtered_skills[filtered_skills["company"] == selected_company]

if selected_location != "Toutes":
    filtered_jobs = filtered_jobs[filtered_jobs["location"] == selected_location]
    filtered_skills = filtered_skills[filtered_skills["location"] == selected_location]

if selected_category != "Toutes":
    filtered_skills = filtered_skills[filtered_skills["category"] == selected_category]

if selected_compliance == "Uniquement avec certification":
    filtered_skills = filtered_skills[filtered_skills["compliance_relevant"] == 1]
elif selected_compliance == "Uniquement générales":
    filtered_skills = filtered_skills[filtered_skills["compliance_relevant"] == 0]

filtered_jobs = filtered_jobs[filtered_jobs['id'].isin(filtered_skills['job_id'].unique())]

# ✅ Gestion des cas vides (amélioration)
if len(filtered_jobs) == 0:
    st.warning("Aucune offre ne correspond à ces filtres. Essayez d'en retirer un.")
    st.stop()

# ============================================================
# INDICATEURS CLÉS AVEC TOOLTIPS (amélioration)
# ============================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📊 Offres",
        len(filtered_jobs),
        delta=f"{len(filtered_jobs[filtered_jobs['status'] == 'open'])} ouvertes",
        help="Nombre total d'offres d'emploi analysées"
    )

with col2:
    st.metric(
        "💡 Compétences uniques",
        filtered_skills["skill_name"].nunique(),
        help="Nombre de compétences différentes identifiées dans les offres"
    )

with col3:
    avg = round(len(filtered_skills) / len(filtered_jobs) if len(filtered_jobs) > 0 else 0, 1)
    st.metric(
        "📈 Compétences / offre",
        avg,
        help="Nombre moyen de compétences demandées par offre"
    )

with col4:
    pct = round(
        len(filtered_skills[filtered_skills['compliance_relevant'] == 1]) / len(filtered_skills) * 100
        if len(filtered_skills) > 0 else 0, 1
    )
    st.metric(
        "🔒 Certification/Norme",
        f"{pct}%",
        help="% de compétences liées à une norme ou certification obligatoire (ex: ISO 45001)"
    )

st.markdown("---")

# ============================================================
# LAYOUT PRINCIPAL
# ============================================================
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 🏆 Top 15 compétences demandées")
    
    top_skills = (
        filtered_skills.groupby("skill_name")
        .size()
        .reset_index(name="nb")
        .sort_values("nb", ascending=False)
        .head(15)
    )
    
    if len(top_skills) > 0:
        fig = px.bar(
            top_skills.sort_values("nb"),
            x="nb", y="skill_name",
            orientation="h",
            labels={"nb": "Occurrences", "skill_name": "Compétence"},
            color="nb",
            color_continuous_scale="Blues",
            title=""
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=420,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### 🤖 Assistant IA")
    st.markdown('<p style="color: #7A8FA0; font-size: 0.85rem;">Posez une question sur les données</p>', unsafe_allow_html=True)
    
    suggestions = [
        "Top 5 compétences techniques ?",
        "Quelle entreprise recrute le plus ?",
        "Compétences avec certification ?",
        "Comparer les entreprises ?"
    ]
    
    for suggestion in suggestions:
        if st.button(suggestion, key=f"sugg_{suggestion[:10]}", use_container_width=True):
            st.session_state['question'] = suggestion
    
    question = st.text_input(
        "Votre question",
        value=st.session_state.get('question', ''),
        placeholder="Ex: Quelles compétences sont les plus demandées ?"
    )
    
    if st.button("🔍 Analyser", type="primary", use_container_width=True):
        if question:
            with st.spinner("Analyse en cours..."):
                response = query_groq(question, filtered_skills, filtered_jobs)
                st.markdown(f"""
                    <div class="chat-message-ai">
                        <b>🤖 Réponse :</b><br>{response}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Entrez une question")

st.markdown("---")

# ============================================================
# VUE PAR CATÉGORIE
# ============================================================
st.markdown("### 📋 Top compétences par catégorie")

categories_list = ['Operational & Technical', 'Health, Safety & Risk Management', 'Digital & Automation', 'Soft & Leadership']
cols = st.columns(4)

for i, cat in enumerate(categories_list):
    with cols[i]:
        st.markdown(f"**{cat}**")
        cat_skills = filtered_skills[filtered_skills["category"] == cat]
        top_cat = cat_skills.groupby("skill_name").size().reset_index(name="nb").sort_values("nb", ascending=False).head(5)
        
        if len(top_cat) > 0:
            for _, row in top_cat.iterrows():
                st.markdown(f"- {row['skill_name']} **({row['nb']})**")
        else:
            st.caption("_Aucune donnée_")

st.markdown("---")

# ============================================================
# MATRICE
# ============================================================
st.markdown("### 🏢 Matrice Entreprise vs Catégorie")

matrix = pd.crosstab(
    filtered_skills['company'],
    filtered_skills['category']
)

if not matrix.empty:
    fig_heatmap = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[
            [0, '#f0f4f8'],
            [0.5, '#8ba3c4'],
            [1, '#1A3A5C']
        ],
        labels={'x': 'Catégorie', 'y': 'Entreprise', 'color': 'Occurrences'},
        zmin=0,
        zmax=matrix.max().max() + 5
    )
    
    fig_heatmap.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(size=14, color='#1A3A5C'),
        xaxis=dict(tickangle=30, tickfont=dict(size=13)),
        yaxis=dict(tickfont=dict(size=13)),
        coloraxis_colorbar=dict(
            title=dict(text='Occurrences', font=dict(size=12))
        )
    )
    
    fig_heatmap.update_traces(
        textfont=dict(size=16, color='black'),
        hovertemplate=(
            '<b>%{y}</b> / <b>%{x}</b><br>'
            'Occurrences: <b>%{z}</b><br>'
            '<extra></extra>'
        ),
        texttemplate='%{z}'
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    total_by_company = matrix.sum(axis=1).sort_values(ascending=False)
    top_cat = matrix.sum(axis=0).sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"🏢 **{total_by_company.index[0]}** : {total_by_company.iloc[0]} compétences")
    with col2:
        st.caption(f"📂 **{top_cat.index[0]}** : {top_cat.iloc[0]} compétences")
else:
    st.caption("_Aucune donnée_")

st.markdown("---")

# ============================================================
# ÉVOLUTION + RÉPARTITION
# ============================================================
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Évolution des offres")
    
    if 'date_scraped' in filtered_jobs.columns and not filtered_jobs['date_scraped'].isna().all():
        filtered_jobs['date_scraped'] = pd.to_datetime(filtered_jobs['date_scraped'])
        daily_jobs = filtered_jobs.groupby(
            filtered_jobs['date_scraped'].dt.date
        ).size().reset_index(name='nb_offres')
        
        if len(daily_jobs) > 1:
            fig_evo = px.line(
                daily_jobs,
                x='date_scraped',
                y='nb_offres',
                title="",
                labels={'date_scraped': 'Date', 'nb_offres': 'Nb offres'},
                markers=True,
                color_discrete_sequence=['#1A3A5C']
            )
            fig_evo.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_evo, use_container_width=True)
        else:
            st.caption("_Données temporelles limitées_")
    else:
        st.caption("_Aucune donnée temporelle_")

with col2:
    st.markdown("### 📊 Répartition par catégorie")
    
    category_counts = filtered_skills.groupby("category").size().reset_index(name="nb")
    
    if len(category_counts) > 0:
        fig_pie = px.pie(
            category_counts,
            values="nb",
            names="category",
            title="",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            insidetextorientation='radial'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ============================================================
# LISTE DES OFFRES
# ============================================================
st.markdown("### 📋 Offres analysées")

jobs_with_skills = filtered_jobs.copy()
jobs_with_skills['nb_skills'] = jobs_with_skills['id'].map(
    filtered_skills.groupby('job_id').size()
).fillna(0).astype(int)

col_download, _ = st.columns([1, 3])
with col_download:
    st.download_button(
        label="📥 Télécharger (CSV)",
        data=filtered_jobs.to_csv(index=False).encode("utf-8"),
        file_name=f"offres_filtrees_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.dataframe(
    jobs_with_skills[['title', 'company', 'location', 'source', 'nb_skills']],
    use_container_width=True,
    hide_index=True,
    column_config={
        'title': 'Poste',
        'company': 'Entreprise',
        'location': 'Localisation',
        'source': 'Source',
        'nb_skills': 'Compétences'
    }
)

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
    <div class="footer">
        ⛏️ Mining Skills Intelligence • {len(jobs_df)} offres analysées • 
        Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
""", unsafe_allow_html=True)