# Placeholder for citation_utils.py
import re

def extract_doi(text):
    """
    Extrait les identifiants DOI (Digital Object Identifier) d’un texte.

    Args:
        text (str): Texte d’entrée.

    Returns:
        list[str]: Liste des DOI détectés (avec lien complet).
    """
    pattern = r'(https?://doi\.org/[^\s\)]+)'
    return re.findall(pattern, text)


def extract_urls(text):
    """
    Extrait toutes les URLs génériques dans un texte.

    Args:
        text (str): Texte d’entrée.

    Returns:
        list[str]: Liste des URLs.
    """
    pattern = r'(https?://[^\s\)]+)'
    return re.findall(pattern, text)


def extract_citation_patterns(text):
    """
    Détecte des formats classiques de citations bibliographiques.

    Args:
        text (str): Texte scientifique contenant potentiellement des références.

    Returns:
        list[str]: Citations textuelles probables.
    """
    patterns = [
        # Format standard auteur-date
        r'\b[A-ZÉÈÀÂÇÏÎ][a-zéèàâçïî]+(?: et al\.)?,?\s*\d{4}\b',  # Dupont 2020, Dupont,2020, Élise et al. 2021
        r'\([A-ZÉÈÀÂÇÏÎ][a-zéèàâçïî]+(?: et al\.)?,?\s*\d{4}\)',  # (Dupont 2020), (Élise et al., 2021)
        
        # Formats avec séparateurs multiples auteurs
        r'\([A-ZÉÈÀÂÇÏÎ][a-zéèàâçïî]+(?:,? (?:&|and|et) [A-ZÉÈÀÂÇÏÎ][a-zéèàâçïî]+)+,?\s*\d{4}\)',  # (Dupont & Martin 2020), (Élise, Martin et Durand, 2021)
        
        # Citations numériques
        r'\[\d+\]',                                      # [1], [42]
        r'\b\d{4}[a-z]?\b',                              # 2020, 2021a (pour les distinctions)
        r'\b(?:cf\.?|voir|see)\s\[\d+(?:\,\s?\d+)*\]',   # cf. [1, 3, 5], voir [6-8]
        
        # Citations avec exposants
        r'\b\d+(?:[eè]me?|ère|nd|rd|th)\b',             # 1er, 2e, 3ème, 4th
        r'\b(?:ref|n°|no)\.?\s*\d+\b',                  # ref. 42, n°3, no. 5
        
        # Formats de références complexes
        r'\b(?:vol|tome|chapter|chapitre)\.?\s*\d+',    # vol. 3, tome 2, chapter 4
        r'\bp\.\s*\d+(?:\-\d+)?',                       # p. 42, p. 12-15
        r'\b(?:pp|pages?)\.?\s*\d+\-\d+',               # pp. 23-25, pages 42-45
        
        # DOI et identifiants
        r'\b10\.[0-9]{4,9}/[-._;()/:A-Za-z0-9]+\b',     # DOI standard
        r'\barXiv:\d{4}\.\d{4,5}(v\d+)?\b',             # arXiv:2012.12345v2
        
        # Autres formats académiques
        r'\b(?:fig|figure|table|tab)\.?\s*\d+[a-z]?\b', # fig. 3, table 2a
        r'\b(?:eq|equation)\.?\s*\d+\b',                # eq. 5, equation 3
        
        # Gestion des suffixes
        r'\b(?:ibid|idem|op\.\s?cit|loc\.\s?cit)\b',    # ibid., op. cit.
        
        # Citations en exposant
        r'\^\[\d+\]',                                   # ^[1], ^[42]
        r'\^\d+',                                       # ^12, ^3
        r'<sup>\d+</sup>',                              # <sup>1</sup>
        
        # Formats de conférence
        r'\b[A-Z]{2,}\s\d{4}\b',                       # ACL 2020, EMNLP 2021
        r'\b(?:Proc|Conf)\.\s[A-Z][\w\s]+ \d{4}\b'     # Proc. ACL 2020
    ]

    citations = []
    for pat in patterns:
        citations += re.findall(pat, text)

    return citations

