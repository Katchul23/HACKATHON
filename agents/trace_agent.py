# Placeholder for trace_agent.py
import re
import requests

class TraceAgent:
    def __init__(self, enrich_with_crossref=False):
        self.name = "TraceAgent"
        self.enrich_with_crossref = enrich_with_crossref

    def trace_source(self, citation_text):
        """
        Tente d'identifier ou de reconstruire la source d'une citation de données secondaires.

        Args:
            citation_text (str): Texte contenant une mention de données.

        Returns:
            str | dict: URL simple, ou dict enrichi avec les métadonnées Crossref si activé.
        """
        citation_text = citation_text.lower()

        # 🔹 Institutions connues (FR/EN)
        known_sources = {
            "insee": "https://www.insee.fr",
            "banque mondiale": "https://data.worldbank.org",
            "world bank": "https://data.worldbank.org",
            "fao": "https://www.fao.org/statistics",
            "who": "https://www.who.int/data",
            "oms": "https://www.who.int/data",
            "unesco": "https://data.uis.unesco.org",
            "ipcc": "https://www.ipcc.ch/data",
            "undp": "https://data.undp.org",
            "eurostat": "https://ec.europa.eu/eurostat"
        }

        for keyword, url in known_sources.items():
            if keyword in citation_text:
                return url

        # 🔸 DOI détecté
        doi_match = re.search(r"(https?://doi\.org/[^\s)\"']+)", citation_text)
        if doi_match:
            doi_url = doi_match.group(1)
            if self.enrich_with_crossref:
                return enrich_doi_with_crossref(doi_url)
            return doi_url

        # 🔸 URL générique détectée
        url_match = re.search(r"https?://[^\s)\"']+", citation_text)
        if url_match:
            return url_match.group(0)

        return "Source inconnue"


def enrich_doi_with_crossref(doi_url):
    """
    Utilise l'API Crossref pour récupérer des métadonnées bibliographiques à partir d’un DOI.

    Args:
        doi_url (str): URL de type https://doi.org/...

    Returns:
        dict: Métadonnées enrichies (titre, auteurs, etc.) ou erreur.
    """
    try:
        if "doi.org/" in doi_url:
            doi = doi_url.split("doi.org/")[1]
        else:
            return {}

        response = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10)
        if response.status_code != 200:
            return {}

        data = response.json()["message"]

        metadata = {
            "titre": data.get("title", [""])[0],
            "auteurs": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in data.get("author", [])],
            "journal": data.get("container-title", [""])[0],
            "annee": data.get("published-print", {}).get("date-parts", [[None]])[0][0]
                      or data.get("published-online", {}).get("date-parts", [[None]])[0][0],
            "editeur": data.get("publisher", ""),
            "doi": doi_url
        }

        return metadata

    except Exception as e:
        return {"erreur": str(e)}


