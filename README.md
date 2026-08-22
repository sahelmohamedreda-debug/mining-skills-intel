# \# Mining Skills Intel

# 

# Système automatisé de collecte et d'analyse des compétences demandées dans les offres d'emploi du secteur minier / mining-tech.

# 

# \*\*Projet réalisé dans le cadre d'un stage — TOD (Talent, Organization \& Development), Groupe OCP — SBU Mining.\*\*

# 

# \---

# 

# \## ⚠️ Note importante sur la formulation

# 

# Ce projet analyse les compétences \*\*demandées\*\* par les employeurs dans leurs offres d'emploi — pas les compétences réellement disponibles chez les travailleurs. Il ne s'agit donc \*\*pas\*\* d'un véritable écart offre/demande ("skills gap"), mais uniquement d'une photographie de la demande exprimée par un échantillon de 5 entreprises. Cette nuance est rappelée partout dans le code, la base de données et le dashboard.

# 

# \---

# 

# \## Contexte

# 

# Le projet répond à une question simple : \*quelles compétences les entreprises minières et mining-tech recherchent-elles aujourd'hui ?\* Pour y répondre, un pipeline automatisé :

# 

# 1\. Collecte les offres d'emploi publiées par 5 entreprises via leurs plateformes de recrutement (ATS) publiques

# 2\. Extrait les compétences mentionnées dans chaque offre via un modèle de langage (LLM)

# 3\. Classe ces compétences dans 4 catégories métier définies

# 4\. Présente les résultats dans un dashboard interactif

# 

# \---

# 

# \## Architecture du projet

mining-skills-intel/

├── .github/workflows/ # Automatisation GitHub Actions (pipeline quotidien)

├── .streamlit/ # Configuration du thème du dashboard

├── data/ # Base de données SQLite (jobs.db)

├── docs/ # Documentation technique détaillée (par étape)

├── src/

│ ├── collectors/ # Scripts de collecte des offres (par ATS)

│ │ ├── common.py # Fonctions partagées (nettoyage, stockage)

│ │ ├── greenhouse.py # Collector pour l'ATS Greenhouse

│ │ ├── workable.py # Collector pour l'ATS Workable

│ │ ├── ashby.py # Collector pour l'ATS Ashby

│ │ ├── rippling.py # Collector pour l'ATS Rippling

│ │ ├── sources\_config.py # Liste des entreprises suivies

│ │ ├── run\_all.py # Lance la collecte sur toutes les sources

│ │ └── mark\_closed\_jobs.py # Marque les offres disparues comme fermées

│ ├── db/ # Base de données et utilitaires

│ │ ├── db.py # Connexion, création, insertion

│ │ ├── schema.sql # Schéma de la table jobs

│ │ └── init\_extraction\_tables.py # Crée les tables skills/job\_skills

│ ├── extraction/ # Extraction des compétences par LLM

│ │ ├── extract\_skills.py # Appel API + parsing JSON

│ │ ├── extract\_batch.py # Traite un batch d'offres

│ │ └── run\_full\_extraction.py # Boucle sur tous les batches restants

│ ├── analysis/ # Requêtes d'analyse SQL/pandas

│ │ └── analyze\_skills.py

│ └── dashboard/ # Application Streamlit

│ └── app.py

├── tests/ # Tests automatisés

├── requirements.txt # Dépendances Python

└── README.md



\---



\## Installation



\### Prérequis

\- Python 3.11 ou supérieur

\- Git



\### Étapes



1\. \*\*Cloner le repo\*\*

```bash

git clone https://github.com/sahelmohamedreda-debug/mining-skills-intel.git

cd mining-skills-intel

```



2\. \*\*Créer et activer un environnement virtuel\*\*

```bash

python -m venv venv

\# Windows

venv\\Scripts\\Activate.ps1

\# Mac/Linux

source venv/bin/activate

```



3\. \*\*Installer les dépendances\*\*

```bash

pip install -r requirements.txt

```



4\. \*\*Configurer les clés API\*\*



Créer un fichier `.env` à la racine du projet :





