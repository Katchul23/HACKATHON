import re

def extract_doi(text: str) -> str:
    """
    Extrait correctement un DOI, même complexe.
    """
    if not text:
        return ""

    # DOI = 10.<4-9 chiffres>/<chaîne alphanum + ponctuation sauf espace/fin de phrase>
    doi_pattern = r'\b10\.\d{4,9}/[\w.\-;()/:]+'
    match = re.search(doi_pattern, text, re.IGNORECASE)
    return match.group(0).strip().rstrip(".,;") if match else ""


def interpret_prompt(prompt: str) -> dict:
    prompt = prompt.lower().strip()
    doi = extract_doi(prompt)

    # Résumé demandé
    if "résume" in prompt or "résumé" in prompt:
        return {"action": "summary"}

    # Requête spécifique sur type de citation
    if "citation" in prompt or "donnée" in prompt:
        if "primaire" in prompt or "originale" in prompt:
            type_cit = "primaire"
        elif "secondaire" in prompt or "réutilisée" in prompt:
            type_cit = "secondaire"
        else:
            type_cit = None

        if not doi:
            return {
                "action": "citations" if type_cit else "awaiting_doi",
                "type": type_cit,
                "doi": None,
                "expecting": "doi",
                "pending_prompt": prompt
            }

        return {
            "action": "citations" if type_cit else "show_citations",
            "type": type_cit,
            "source": doi  # ✅ Corrigé ici
        }

    # Cas : "Montre-moi les citations", "Quelles données sont citées ?", etc.
    if any(word in prompt for word in ["montre", "affiche", "vois", "voir", "liste", "cité", "citées", "utilisé", "mentionné"]):
        if doi:
            return {"action": "show_citations", "source": doi}
        else:
            return {
                "action": "awaiting_doi",
                "pending_prompt": prompt
            }

    # Cas générique : DOI ou long texte → lancer analyse
    if doi or len(prompt.split()) > 10:
        return {"action": "analyse", "source": doi or prompt}

    return {"action": "unknown"}

