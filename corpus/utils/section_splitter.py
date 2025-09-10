import re

def segment_sections(text, lang="auto"):
    """
    Découpe un texte scientifique en sections classiques (français ou anglais), y compris titres numérotés et sections supplémentaires comme Résumé ou Abstract.

    Args:
        text (str): Texte brut extrait du PDF ou HTML.
        lang (str): Langue détectée ('fr', 'en', 'auto').

    Returns:
        dict: Sections structurées : abstract, introduction, méthodologie, résultats, discussion, conclusion.
    """
    sections = {
        "abstract": "",
        "introduction": "",
        "méthodologie": "",
        "résultats": "",
        "discussion": "",
        "conclusion": ""
    }

    if lang == "fr":
        keywords = {
            "abstract": ["résumé"],
            "introduction": ["introduction"],
            "méthodologie": ["méthodes", "méthodologie", "proposition", "outil", "mise en œuvre", "implémentation"],
            "résultats": ["résultats", "résultat", "expérience", "retour", "cas d'étude"],
            "discussion": ["discussion"],
            "conclusion": ["conclusion"]
        }
    elif lang == "en":
        keywords = {
            "abstract": ["abstract"],
            "introduction": ["introduction", "background"],
            "méthodologie": ["methods", "methodology", "proposed approach", "implementation", "tool"],
            "résultats": ["results", "findings", "experiment", "evaluation", "case study"],
            "discussion": ["discussion"],
            "conclusion": ["conclusion", "conclusions"]
        }
    else:
        keywords = {
            "abstract": ["abstract", "résumé"],
            "introduction": ["introduction", "background"],
            "méthodologie": ["methods", "méthodologie", "proposition", "tool", "mise en œuvre", "implementation"],
            "résultats": ["results", "résultats", "findings", "retour", "case study", "expérience"],
            "discussion": ["discussion"],
            "conclusion": ["conclusion", "conclusions"]
        }

    # Titres numérotés ou majuscules sur une ligne propre
    numbered_or_upper = re.compile(r"\n?\s*(\d{1,2}(\.\d+)*([\.:\-\)])?\s+)?([A-Z\u00C0-\u017F\s]{3,100}|[A-Za-z\u00C0-\u017F\s]{3,100})\n", re.IGNORECASE)
    matches = list(numbered_or_upper.finditer(text))
    segments = []

    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        segment_text = text[start:end].strip()
        title = match.group(0).strip()
        segments.append((title, segment_text))

    # Attribution heuristique
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
