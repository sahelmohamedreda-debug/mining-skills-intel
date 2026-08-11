import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
PROMPT_TEMPLATE = """Extract skills from this job posting at a MINING/MINERALS company. Return ONLY valid JSON.

Job Title: {title}
Job Description: {description}

IMPORTANT: This job is at a mining/minerals company. ANY technical, digital, engineering, or operational skill mentioned counts as relevant — including software, AI, cloud, data, automation, engineering, or project skills — because they are applied within the mining industry context.

ONLY put in "out_of_scope": skills that are purely corporate/administrative and unrelated to any technical or operational function — such as pure legal, pure accounting/finance, pure general HR, executive assistant tasks.

Categories:
- Operational & Technical: drilling, mining, ore processing, geology, engineering
- Health, Safety & Risk Management: safety, risk, compliance
- Digital & Automation: software, AI, data, cloud, automation, digital transformation, IoT
- Soft & Leadership: communication, leadership, project management, collaboration

Return this exact JSON:
{{"skills": [{{"skill": "skill name", "category": "one of the 4 categories above", "compliance_relevant": true or false}}], "out_of_scope": ["purely corporate/admin skill"]}}

Return ONLY JSON, nothing else."""

def extract_skills_from_description(job_title: str, job_description: str) -> dict:
    """Extract skills from a job description using Groq."""
    
    # Retire le paragraphe générique "About the Company" (répété sur toutes les offres KoBold)
    description_clean = job_description
    if "About the Company" in description_clean:
        parts = description_clean.split("About the Company")
        # Garde la dernière occurrence (après le blabla générique sur l'entreprise)
        description_clean = parts[-1]
    
    prompt = PROMPT_TEMPLATE.format(
        title=job_title[:100], 
        description=description_clean[:3000]  # Augmenté de 1500 à 3000
    )
    
    try:
        response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",  # Au lieu de meta-llama/Llama-3.3-70B-Instruct
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=800,
)
        
        response_text = response.choices[0].message.content.strip()
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            result = json.loads(json_str)
            
            if "skills" not in result:
                result["skills"] = []
            if "out_of_scope" not in result:
                result["out_of_scope"] = []
            
            return result
        
        return {"skills": [], "out_of_scope": []}
        
    except json.JSONDecodeError:
        return {"skills": [], "out_of_scope": []}
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate_limit" in error_str:
            return {"error": "Rate limit: " + error_str}
        return {"skills": [], "out_of_scope": []}