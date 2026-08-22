"""Tests du parsing JSON des réponses LLM (cas limites)."""
import json


def parse_llm_response(response_text: str) -> dict:
    """
    Reproduit la logique de parsing utilisée dans extract_skills.py :
    extrait le JSON entre la première { et la dernière }.
    """
    start = response_text.find('{')
    end = response_text.rfind('}') + 1

    if start >= 0 and end > start:
        json_str = response_text[start:end]
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError:
            return {"skills": [], "out_of_scope": []}
    else:
        return {"skills": [], "out_of_scope": []}

    if "skills" not in result:
        result["skills"] = []
    if "out_of_scope" not in result:
        result["out_of_scope"] = []

    return result


def test_parsing_empty_string():
    """Une réponse vide ne doit jamais faire planter le parsing."""
    result = parse_llm_response("")
    assert result == {"skills": [], "out_of_scope": []}


def test_parsing_valid_json():
    """Un JSON valide doit être correctement parsé."""
    raw = '{"skills": [{"skill": "Python", "category": "Digital & Automation", "compliance_relevant": false}], "out_of_scope": []}'
    result = parse_llm_response(raw)
    assert len(result["skills"]) == 1
    assert result["skills"][0]["skill"] == "Python"


def test_parsing_json_with_surrounding_text():
    """Le JSON entouré de texte parasite doit quand même être extrait."""
    raw = 'Voici le résultat:\n{"skills": [], "out_of_scope": ["comptabilité"]}\nVoilà !'
    result = parse_llm_response(raw)
    assert result["out_of_scope"] == ["comptabilité"]


def test_parsing_malformed_json():
    """Un JSON mal formé doit renvoyer une structure vide, pas planter."""
    raw = '{"skills": [{"skill": "Python", "category": ...'  # JSON tronqué/invalide
    result = parse_llm_response(raw)
    assert result == {"skills": [], "out_of_scope": []}


def test_parsing_no_json_at_all():
    """Une réponse sans aucune accolade doit renvoyer une structure vide."""
    raw = "Je ne peux pas répondre à cette question."
    result = parse_llm_response(raw)
    assert result == {"skills": [], "out_of_scope": []}


if __name__ == "__main__":
    test_parsing_empty_string()
    test_parsing_valid_json()
    test_parsing_json_with_surrounding_text()
    test_parsing_malformed_json()
    test_parsing_no_json_at_all()
    print("✅ Tous les tests de parsing JSON passent")