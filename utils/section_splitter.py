import re

def split_sections(text, lang="auto"):
    """
    Découpe un texte scientifique en sections classiques (français ou anglais), y compris titres numérotés.

    Args:
        text (str): Texte brut extrait du PDF.
        lang (str): Langue détectée ('fr', 'en', 'auto').

    Returns:
        dict: Sections structurées : introduction, méthodologie, résultats, discussion, conclusion.
    """
    sections = {
        "introduction": "",
        "méthodologie": "",
        "résultats": "",
        "discussion": "",
        "conclusion": ""
    }

    if lang == "fr":
        keywords = {
            "introduction": ["introduction"],
            "méthodologie": ["méthodes", "méthodologie", "proposition", "outil", "mise en œuvre", "implémentation"],
            "résultats": ["résultats", "résultat", "expérience", "retour", "cas d'étude"],
            "discussion": ["discussion"],
            "conclusion": ["conclusion"]
        }
    elif lang == "en":
        keywords = {
            "introduction": ["introduction", "background"],
            "méthodologie": ["methods", "methodology", "proposed approach", "implementation", "tool"],
            "résultats": ["results", "findings", "experiment", "evaluation", "case study"],
            "discussion": ["discussion"],
            "conclusion": ["conclusion", "conclusions"]
        }
    else:
        keywords = {
            "introduction": ["introduction", "background"],
            "méthodologie": ["methods", "méthodes", "methodology", "proposition", "outil", "mise en œuvre", "implementation"],
            "résultats": ["results", "résultats", "findings", "retour", "case study", "expérience"],
            "discussion": ["discussion"],
            "conclusion": ["conclusion", "conclusions"]
        }

    # Extraction des blocs à partir des titres numérotés ou des mots-clés classiques
    numbered_section_pattern = re.compile(r"\n?\s*(\d{1,2}(\.\d+)*)([\.\-:]|\))?\s+([^\n]{3,100})", re.IGNORECASE)
    matches = list(numbered_section_pattern.finditer(text))
    segments = []

    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        segment_text = text[start:end].strip()
        title = match.group(0).strip()
        segments.append((title, segment_text))

    # Attribution par heuristique
    for title, content in segments:
        title_lower = title.lower()
        content_lower = content.lower()

        assigned = False
        for section, cues in keywords.items():
            if any(cue in title_lower for cue in cues) or any(cue in content_lower[:300] for cue in cues):
                sections[section] += f"\n{title}\n{content}\n"
                assigned = True
                break

        if not assigned:
            sections["discussion"] += f"\n{title}\n{content}\n"  # fallback

    return sections
