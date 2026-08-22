# src/dashboard/app.py

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px
from datetime import datetime
import os

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="Compétences minières — Tableau de bord",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.db"

# ============================================================
# STYLE — IDENTITÉ "CAROTTE DE FORAGE"
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;800&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;600&display=swap');

.stApp {
    background: #12181D;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #EDEAE2;
}

h1, h2, h3, .main-header {
    font-family: 'Big Shoulders Display', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px;
    color: #EDEAE2 !important;
    text-transform: uppercase;
}

.strata-bar {
    height: 6px;
    width: 100%;
    background: linear-gradient(90deg,
        #5C8B7C 0%, #5C8B7C 20%,
        #D4A24C 20%, #D4A24C 45%,
        #3A4A52 45%, #3A4A52 60%,
        #8B6F47 60%, #8B6F47 80%,
        #5C8B7C 80%, #5C8B7C 100%);
    border-radius: 3px;
    margin: 0 0 1.8rem 0;
}

.main-header {
    font-size: 2.6rem;
    margin-bottom: 0.1rem;
    line-height: 1.05;
}

.header-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #5C8B7C;
    margin-bottom: 0.4rem;
}

.sub-header {
    font-size: 1.05rem;
    color: #8B93A0;
    margin-bottom: 1.2rem;
    font-weight: 400;
}

.sample-card {
    background: #1C242B;
    border: 1px solid #2A343C;
    border-left: 3px solid #5C8B7C;
    padding: 1.1rem 1.3rem;
    border-radius: 4px;
    position: relative;
    transition: border-color 0.25s ease, transform 0.25s ease;
    margin-bottom: 0.8rem;
}

.sample-card:hover {
    border-left-color: #D4A24C;
    transform: translateX(2px);
}

.sample-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #8B93A0;
    margin-bottom: 0.4rem;
}

.sample-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.1rem;
    font-weight: 600;
    color: #EDEAE2;
    line-height: 1;
}

.sample-label {
    font-size: 0.82rem;
    color: #8B93A0;
    margin-top: 0.35rem;
}

.sample-delta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #5C8B7C;
    margin-top: 0.5rem;
    display: inline-block;
}

section[data-testid="stSidebar"] {
    background: #1C242B !important;
    border-right: 1px solid #2A343C;
}

section[data-testid="stSidebar"] .stSelectbox label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #8B93A0 !important;
}

.stExpander {
    border: 1px solid #2A343C !important;
    border-radius: 4px !important;
    background: #1C242B !important;
}

div[data-testid="stAlertContainer"] {
    background: #241E14 !important;
    border-left: 3px solid #D4A24C !important;
    border-radius: 4px !important;
}

.stButton > button {
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    border: 1px solid #2A343C !important;
    background: #1C242B !important;
    color: #EDEAE2 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    border-color: #5C8B7C !important;
    color: #5C8B7C !important;
}

.stButton > button[kind="primary"] {
    background: #5C8B7C !important;
    color: #12181D !important;
    border: none !important;
}

.stButton > button[kind="primary"]:hover {
    background: #6FA088 !important;
}

.stDataFrame {
    border: 1px solid #2A343C !important;
    border-radius: 4px !important;
}

.section-marker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #5C8B7C;
    letter-spacing: 1px;
    margin-bottom: -0.3rem;
}

.footer {
    text-align: center;
    padding: 1.5rem;
    color: #5A6470;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.5px;
    border-top: 1px solid #2A343C;
    margin-top: 2rem;
}

hr {
    border: none;
    height: 1px;
    background: #2A343C;
    margin: 2rem 0;
}

/* ====== ACCESSIBILITÉ ====== */
:focus-visible {
    outline: 2px solid #D4A24C !important;
    outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
    .sample-card {
        transition: none !important;
    }
    .sample-card:hover {
        transform: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# EXTRACTION PAYS
# ============================================================
def extract_country(location):
    """Extrait le pays depuis une localisation"""
    if pd.isna(location) or location == "":
        return "Non spécifié"
    parts = location.split(',')
    if len(parts) >= 3:
        return parts[-1].strip()
    elif len(parts) == 2:
        return parts[-1].strip()
    return location.strip()

# ============================================================
# CONNEXION À LA BASE
# ============================================================
@st.cache_data(ttl=3600)
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
    
    # Ajouter la colonne country
    jobs['country'] = jobs['location'].apply(extract_country)
    skills['country'] = skills['location'].apply(extract_country)
    
    return jobs, skills

jobs_df, skills_df = load_data()

if jobs_df.empty:
    st.error("⚠️ Aucune donnée disponible. Vérifie que la base de données contient des offres.")
    st.stop()

# ============================================================
# FONCTION EXPORT RAPPORT HTML
# ============================================================
def generate_report_html(jobs_data: pd.DataFrame, skills_data: pd.DataFrame) -> str:
    """Génère un rapport HTML avec les métriques et graphiques"""
    
    top_skills = skills_data['skill_name'].value_counts().head(10)
    cat_dist = skills_data['category'].value_counts()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Rapport compétences minières</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #12181D; color: #EDEAE2; padding: 2rem; max-width: 900px; margin: 0 auto; }}
            h1 {{ font-family: 'Big Shoulders Display', sans-serif; color: #D4A24C; font-size: 2.5rem; }}
            h2 {{ font-family: 'Big Shoulders Display', sans-serif; color: #5C8B7C; margin-top: 2rem; }}
            .metric {{ background: #1C242B; padding: 1rem 1.5rem; border-left: 4px solid #5C8B7C; margin: 0.5rem 0; border-radius: 4px; }}
            .metric-value {{ font-size: 2.2rem; font-weight: 700; color: #EDEAE2; }}
            .metric-label {{ color: #8B93A0; font-size: 0.9rem; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ background: #1C242B; padding: 0.5rem 1rem; margin: 0.3rem 0; border-radius: 4px; border-left: 2px solid #D4A24C; }}
            hr {{ border: 1px solid #2A343C; margin: 2rem 0; }}
            .footer {{ color: #5A6470; font-size: 0.8rem; margin-top: 2rem; text-align: center; border-top: 1px solid #2A343C; padding-top: 1.5rem; }}
            .badge {{ display: inline-block; background: #5C8B7C; color: #12181D; padding: 0.1rem 0.6rem; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }}
        </style>
    </head>
    <body>
        <h1>⛏️ Rapport — Compétences demandées</h1>
        <p style="color: #8B93A0;">Secteur minier • {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <hr>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div class="metric">
                <div class="metric-value">{len(jobs_data)}</div>
                <div class="metric-label">📊 Offres analysées</div>
            </div>
            <div class="metric">
                <div class="metric-value">{skills_data['skill_name'].nunique()}</div>
                <div class="metric-label">💡 Compétences uniques</div>
            </div>
        </div>
        
        <h2>🏆 Top 10 compétences</h2>
        <ul>
    """
    for skill, count in top_skills.items():
        html += f"<li>{skill} <span class='badge'>{count}</span></li>"
    
    html += f"""
        </ul>
        
        <h2>📊 Répartition par catégorie</h2>
        <ul>
    """
    for cat, count in cat_dist.items():
        html += f"<li>{cat} — {count}</li>"
    
    html += f"""
        </ul>
        
        <hr>
        <div class="footer">
            ⛏️ Mining Skills Intelligence • {len(jobs_data)} offres analysées • Mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
    </body>
    </html>
    """
    return html

# ============================================================
# EN-TÊTE
# ============================================================
st.markdown("""
<div class="header-eyebrow">Rapport de sondage — Marché de l'emploi</div>
<p class="main-header">Compétences demandées<br>secteur minier</p>
""", unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyse des compétences dans les offres d\'emploi collectées</p>', unsafe_allow_html=True)
st.markdown('<div class="strata-bar"></div>', unsafe_allow_html=True)

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
    <div style="text-align: center; padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #2A343C; margin-bottom: 1rem;">
        <span style="font-size: 2rem;">⛏️</span>
        <p style="font-family: 'Big Shoulders Display', sans-serif; color: #EDEAE2; margin: 0.3rem 0 0 0; font-size: 1.2rem; font-weight: 800; text-transform: uppercase;">Mining Skills</p>
        <p style="font-family: 'IBM Plex Mono', monospace; color: #8B93A0; font-size: 0.7rem; margin: 0; letter-spacing: 1px;">Tableau de bord</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Rafraîchir les données", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("### 🔍 Filtres")

companies = ["Toutes"] + sorted(jobs_df["company"].unique().tolist())
selected_company = st.sidebar.selectbox("🏢 Entreprise", companies)

locations = ["Toutes"] + sorted(jobs_df["location"].dropna().unique().tolist())
selected_location = st.sidebar.selectbox("📍 Localisation", locations)

countries = ["Toutes"] + sorted(jobs_df["country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("🌍 Pays", countries)

categories = ["Toutes"] + sorted(skills_df["category"].unique().tolist())
selected_category = st.sidebar.selectbox("📂 Catégorie", categories)

compliance_options = ["Toutes", "Uniquement avec certification", "Uniquement générales"]
selected_compliance = st.sidebar.selectbox("🔒 Type de compétence", compliance_options)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
    <div style="background: #12181D; border: 1px solid #2A343C; padding: 0.8rem; border-radius: 4px; text-align: center;">
        <p style="margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: #8B93A0;">
            📊 <b style="color: #EDEAE2;">{len(jobs_df)}</b> offres totales
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

if selected_country != "Toutes":
    filtered_jobs = filtered_jobs[filtered_jobs["country"] == selected_country]
    filtered_skills = filtered_skills[filtered_skills["country"] == selected_country]

if selected_category != "Toutes":
    filtered_skills = filtered_skills[filtered_skills["category"] == selected_category]

if selected_compliance == "Uniquement avec certification":
    filtered_skills = filtered_skills[filtered_skills["compliance_relevant"] == 1]
elif selected_compliance == "Uniquement générales":
    filtered_skills = filtered_skills[filtered_skills["compliance_relevant"] == 0]

filtered_jobs = filtered_jobs[filtered_jobs['id'].isin(filtered_skills['job_id'].unique())]

if len(filtered_jobs) == 0:
    st.warning("Aucune offre ne correspond à ces filtres. Essayez d'en retirer un.")
    st.stop()

# ============================================================
# INDICATEURS CLÉS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

metrics_data = [
    ("ÉCH-01", "📊", str(len(filtered_jobs)), "Offres analysées",
     f"{len(filtered_jobs[filtered_jobs['status']=='open'])} ouvertes"),
    ("ÉCH-02", "💡", str(filtered_skills["skill_name"].nunique()), "Compétences uniques", None),
    ("ÉCH-03", "📈", str(round(len(filtered_skills)/len(filtered_jobs), 1) if len(filtered_jobs) > 0 else 0), "Compétences / offre", None),
    ("ÉCH-04", "🔒", f"{round(len(filtered_skills[filtered_skills['compliance_relevant']==1])/len(filtered_skills)*100, 1) if len(filtered_skills) > 0 else 0}%", "Certification / norme", None),
]

for col, (tag, icon, value, label, delta) in zip([col1, col2, col3, col4], metrics_data):
    with col:
        delta_html = f'<div class="sample-delta">↳ {delta}</div>' if delta else ""
        st.markdown(f"""
        <div class="sample-card">
            <div class="sample-tag">{tag} — {icon}</div>
            <div class="sample-value">{value}</div>
            <div class="sample-label">{label}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# LAYOUT PRINCIPAL
# ============================================================
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<p class="section-marker">// CLASSEMENT</p>', unsafe_allow_html=True)
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
            color_continuous_scale=["#2A343C", "#5C8B7C"],
            title=""
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=420,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#EDEAE2', family='Inter')
        )
        st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown('<p class="section-marker">// ANALYSE</p>', unsafe_allow_html=True)
    st.markdown("### 📊 Vue d'ensemble")
    
    # Statistiques rapides dans la colonne droite
    st.markdown(f"""
    <div style="background: #1C242B; border: 1px solid #2A343C; padding: 1rem 1.2rem; border-radius: 4px; margin-bottom: 1rem;">
        <p style="font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #5C8B7C; margin: 0;">ENTREPRISES</p>
        <p style="font-size: 1.2rem; font-weight: 600; margin: 0.2rem 0 0 0;">{filtered_jobs['company'].nunique()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: #1C242B; border: 1px solid #2A343C; padding: 1rem 1.2rem; border-radius: 4px; margin-bottom: 1rem;">
        <p style="font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #5C8B7C; margin: 0;">PAYS</p>
        <p style="font-size: 1.2rem; font-weight: 600; margin: 0.2rem 0 0 0;">{filtered_jobs['country'].nunique()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background: #1C242B; border: 1px solid #2A343C; padding: 1rem 1.2rem; border-radius: 4px;">
        <p style="font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #5C8B7C; margin: 0;">COMPÉTENCES TOTALES</p>
        <p style="font-size: 1.2rem; font-weight: 600; margin: 0.2rem 0 0 0;">{len(filtered_skills)}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# VUE PAR CATÉGORIE
# ============================================================
st.markdown('<p class="section-marker">// RÉPARTITION PAR STRATE</p>', unsafe_allow_html=True)
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
st.markdown('<p class="section-marker">// CROISEMENT</p>', unsafe_allow_html=True)
st.markdown("### 🏢 Matrice Entreprise vs Catégorie")

matrix = pd.crosstab(filtered_skills['company'], filtered_skills['category'])

if not matrix.empty:
    fig_heatmap = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=[
            [0, '#1C242B'],
            [0.5, '#3A5A50'],
            [1, '#5C8B7C']
        ],
        labels={'x': 'Catégorie', 'y': 'Entreprise', 'color': 'Occurrences'},
        zmin=0,
        zmax=matrix.max().max() + 5
    )

    fig_heatmap.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(size=14, color='#EDEAE2', family='Inter'),
        xaxis=dict(tickangle=30, tickfont=dict(size=13)),
        yaxis=dict(tickfont=dict(size=13)),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar=dict(title=dict(text='Occurrences', font=dict(size=12)))
    )

    fig_heatmap.update_traces(
        textfont=dict(size=16, color='#EDEAE2'),
        hovertemplate='<b>%{y}</b> / <b>%{x}</b><br>Occurrences: <b>%{z}</b><extra></extra>',
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
    st.markdown('<p class="section-marker">// CHRONOLOGIE</p>', unsafe_allow_html=True)
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
                labels={'date_scraped': 'Date', 'nb_offres': 'Nb offres'},
                markers=True,
                color_discrete_sequence=['#D4A24C']
            )
            fig_evo.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#EDEAE2', family='Inter')
            )
            st.plotly_chart(fig_evo, use_container_width=True)
        else:
            st.caption("_Données temporelles limitées_")
    else:
        st.caption("_Aucune donnée temporelle_")

with col2:
    st.markdown('<p class="section-marker">// PROPORTIONS</p>', unsafe_allow_html=True)
    st.markdown("### 📊 Répartition par catégorie")

    category_counts = filtered_skills.groupby("category").size().reset_index(name="nb")

    if len(category_counts) > 0:
        fig_pie = px.pie(
            category_counts,
            values="nb",
            names="category",
            color_discrete_sequence=["#5C8B7C", "#D4A24C", "#8B6F47", "#3A5A50"]
        )
        fig_pie.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#EDEAE2', family='Inter')
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            insidetextorientation='radial'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ============================================================
# LISTE DES OFFRES + EXPORT
# ============================================================
st.markdown('<p class="section-marker">// JOURNAL</p>', unsafe_allow_html=True)
st.markdown("### 📋 Offres analysées")

jobs_with_skills = filtered_jobs.copy()
jobs_with_skills['nb_skills'] = jobs_with_skills['id'].map(
    filtered_skills.groupby('job_id').size()
).fillna(0).astype(int)

col_download, col_export, _ = st.columns([1, 1, 2])

with col_download:
    st.download_button(
        label="📥 CSV",
        data=filtered_jobs.to_csv(index=False).encode("utf-8"),
        file_name=f"offres_filtrees_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_export:
    st.download_button(
        label="📊 Rapport HTML",
        data=generate_report_html(filtered_jobs, filtered_skills),
        file_name=f"rapport_compétences_{datetime.now().strftime('%Y%m%d')}.html",
        mime="text/html",
        use_container_width=True
    )

st.dataframe(
    jobs_with_skills[['title', 'company', 'location', 'country', 'source', 'nb_skills']],
    use_container_width=True,
    hide_index=True,
    column_config={
        'title': 'Poste',
        'company': 'Entreprise',
        'location': 'Localisation',
        'country': 'Pays',
        'source': 'Source',
        'nb_skills': 'Compétences'
    }
)

# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
    <div class="footer">
        ⛏️ MINING SKILLS INTELLIGENCE — {len(jobs_df)} OFFRES ANALYSÉES — 
        MISE À JOUR: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
""", unsafe_allow_html=True)