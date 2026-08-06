import json
import sys
import time
from pathlib import Path
from groq import Groq
import os
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
from db.db import get_connection

# Initialise le client Groq
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CATEGORIES_DEFINITION = """
Catégories de compétences minières :

1. Operational & Technical : compétences techniques du cœur du métier minier (forage, exploitation, traitement du minerai, géologie, ingénierie)
2. Health, Safety & Risk Management : sécurité des personnes, gestion des risques, conformité réglementaire
3. Digital & Automation : technologies numériques appliquées à la mine (IA, télé-opération, data science, IoT)
4. Soft & Leadership : compétences comportementales et de gestion transversales (communication, leadership, gestion de projet)

Important : si une compétence ne rentre clairement dans aucune des 4 catégories (ex: comptabilité pure, juridique corporate), classe-la simplement pas — ne force pas un classement arbitraire.
"""

PROMPT_INSTRUCTIONS = """Instruction de sortie :
Retourne UNIQUEMENT du JSON valide, sans aucun texte avant ou après. Le JSON doit respecter EXACTEMENT cette structure :

{
    "skills": [
        {"skill": "nom de la compétence", "category": "Operational & Technical" ou "Health, Safety & Risk Management" ou "Digital & Automation" ou "Soft & Leadership", "compliance_relevant": true ou false},
        ...
    ],
    "out_of_scope": ["compétences non-minières ou trop génériques"]
}

⚠️ CRITICAL : Si le poste est purement corporate/administratif (avocat, comptable, RH générales, assistant d'exécutif, etc.), il est probable qu'il n'ait AUCUNE compétence minière. Dans ce cas, retourne un tableau "skills" **vide ou quasi vide**.

Règles STRICTES :
1. Extrais UNIQUEMENT les compétences spécifiquement minières (géologie, forage, traitement du minerai, données géospatiales, HSE, leadership minier...).
2. Les compétences purement CORPORATE/ADMINISTRATIVES — droit (droit du travail, litigation, droit corporate), comptabilité, finances générales, RH administratives, gestion d'assistante — vont UNIQUEMENT dans "out_of_scope", PAS dans "skills".
3. compliance_relevant = true SEULEMENT si la compétence est liée à une norme/certification obligatoire (ISO 45001, permis d'exploitation, certifications HSE). Sinon false.
4. Le champ "category" ne peut JAMAIS être "out_of_scope" — seul le tableau "out_of_scope" à la racine en accueille.
5. Ne mets RIEN en dehors du JSON — pas de texte, pas d'explication."""

def clean_json_response(text):
    """
    Nettoie la réponse pour extraire uniquement le JSON valide
    """
    # Supprime les marqueurs de code markdown
    text = text.strip()
    
    # Si le texte commence par ```, on extrait le contenu entre les backticks
    if text.startswith("```"):
        # Enlève la première ligne (```json ou ```)
        lines = text.split('\n')
        # Supprime la première ligne (```)
        lines = lines[1:]
        # Supprime la dernière ligne si c'est ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = '\n'.join(lines)
    
    return text.strip()

def extract_skills_from_description(job_title: str, job_description: str) -> dict:
    """
    Appelle l'API Groq pour extraire les compétences d'une description de poste.
    Retourne un dictionnaire avec la structure :
    {
        "skills": [
            {"skill": "...", "category": "...", "compliance_relevant": True/False},
            ...
        ],
        "out_of_scope": ["..."] si des compétences non-minières
    }
    """
    
    prompt = f"""Tu es un expert en analyse des compétences minières. Lis cette offre d'emploi et extrais les compétences demandées.

Titre du poste : {job_title}

Description :
{job_description}

---

CATÉGORIES DE RÉFÉRENCE :
{CATEGORIES_DEFINITION}

---

{PROMPT_INSTRUCTIONS}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Modèle Groq disponible gratuitement
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Bas pour être déterministe sur la structure
            max_tokens=1500,
        )
        
        # Récupère le texte brut de la réponse
        response_text = response.choices[0].message.content.strip()
        
        # Nettoie la réponse pour enlever les backticks markdown
        cleaned_text = clean_json_response(response_text)
        
        # Parse le JSON
        try:
            result = json.loads(cleaned_text)
            return result
        except json.JSONDecodeError as e:
            print(f"Erreur parsing JSON : {e}")
            print(f"Réponse brute reçue : {response_text[:500]}")
            print(f"Texte nettoyé : {cleaned_text[:500]}")
            return {"error": "JSON parsing failed", "raw_response": response_text, "cleaned_response": cleaned_text}
    
    except Exception as e:
        print(f"Erreur appel Groq : {e}")
        return {"error": str(e)}


def validate_extraction(result: dict, job_title: str) -> list:
    """
    Valide la structure et la cohérence de l'extraction
    Retourne une liste de warnings
    """
    warnings = []
    
    # Vérifie la structure de base
    if "skills" not in result and "error" not in result:
        warnings.append("Structure invalide: 'skills' manquant")
        return warnings
    
    if "error" in result:
        return warnings
    
    # Vérifie que out_of_scope est un tableau de strings
    if "out_of_scope" in result:
        if not isinstance(result["out_of_scope"], list):
            warnings.append("'out_of_scope' devrait être un tableau")
        else:
            for item in result["out_of_scope"]:
                if not isinstance(item, str):
                    warnings.append(f"'out_of_scope' contient un élément non-string: {item}")
    
    # Vérifie chaque skill
    valid_categories = [
        "Operational & Technical",
        "Health, Safety & Risk Management", 
        "Digital & Automation",
        "Soft & Leadership"
    ]
    
    for i, skill in enumerate(result.get("skills", [])):
        # Vérifie la structure de chaque skill
        if not all(key in skill for key in ["skill", "category", "compliance_relevant"]):
            warnings.append(f"Skill {i}: structure incomplète")
            continue
        
        # Vérifie que la catégorie est valide
        if skill["category"] not in valid_categories:
            warnings.append(f"Skill '{skill['skill']}': catégorie invalide '{skill['category']}'")
        
        # Vérifie que compliance_relevant est un booléen
        if not isinstance(skill["compliance_relevant"], bool):
            warnings.append(f"Skill '{skill['skill']}': compliance_relevant devrait être un booléen")
    
    # Vérifie la cohérence pour les postes non-miniers
    corporate_keywords = ["counsel", "legal", "attorney", "accounting", "finance", "assistant"]
    if any(keyword in job_title.lower() for keyword in corporate_keywords):
        if len(result.get("skills", [])) > 2:  # Tolère max 2 skills pour les postes corporate
            warnings.append(f"Poste corporate '{job_title}': {len(result['skills'])} skills miniers détectés (devrait être ≤2)")
    
    return warnings


if __name__ == "__main__":
    # Test sur 10 offres réelles de la base
    conn = get_connection()
    cursor = conn.execute("SELECT id, title, description FROM jobs LIMIT 5")
    offres = cursor.fetchall()
    conn.close()
    
    print("=== TEST D'EXTRACTION DE COMPÉTENCES (VERSION FINALE) ===\n")
    
    total_warnings = 0
    
    for job_id, title, description in offres:
        print(f"Offre ID {job_id} : {title}")
        print("-" * 60)
        
        result = extract_skills_from_description(title, description)
        
        # Valide le résultat
        warnings = validate_extraction(result, title)
        if warnings:
            print("⚠️  WARNINGS :")
            for warning in warnings:
                print(f"  - {warning}")
            total_warnings += len(warnings)
        
        # Affiche le résultat formaté
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n")
        
        # Petite pause pour respecter la limite de 30 req/min de Groq
        time.sleep(2)
    
    print(f"\n=== RÉSUMÉ ===")
    print(f"Total warnings: {total_warnings}")
    
    # Statistiques rapides
    print(f"\n=== STATISTIQUES RAPIDES ===")
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]
    print(f"Total offres en DB: {total_jobs}")
    
    # Vérifie si les tables skills existent déjà
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('skills', 'job_skills', 'job_out_of_scope')")
    existing_tables = [row[0] for row in cursor.fetchall()]
    if existing_tables:
        print(f"Tables existantes: {', '.join(existing_tables)}")
    else:
        print("Tables d'extraction non créées (seront créées au Jour 9)")
    
    conn.close()