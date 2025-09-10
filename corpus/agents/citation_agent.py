# agents/citation_agent.py
from corpus.utils.citation_utils import extract_doi, extract_urls, extract_citation_patterns

class CitationDetectionAgent:
    def __init__(self):
        self.name = "CitationDetectionAgent"

    def detect_citations(self, text):
        """
        Détecte différentes formes de citations dans un texte scientifique.

        Args:
            text (str): Texte intégral ou section d’un article.

        Returns:
            dict: Résultats structurés (dois, urls, patterns)
        """
        dois = extract_doi(text)
        urls = extract_urls(text)
        refs = extract_citation_patterns(text)

        return {
            "dois": list(set(dois)),
            "urls": list(set(urls)),
            "references": list(set(refs))
        }
