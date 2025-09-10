# services/analyse_service.py

import os
from pathlib import Path
import sys
from pathlib import Path
from corpus.utils.load_source import load_source
from corpus.utils.lang_detector import detect_language
from corpus.utils.section_splitter import segment_sections
from corpus.utils.pdf_parser import parse_pdf
from corpus.agents.trace_agent import enrich_doi_with_crossref
from corpus.agents.classification_agent import ClassificationAgent
from corpus.crew.crew_setup import initialize_agents
from corpus.crew.task_pipeline import run_pipeline

# 👇 Ajoute automatiquement /DataTrace au PYTHONPATH
BASE_DIR = Path(__file__).resolve().parents[2]  # ← /DataTrace
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


def clean_text(text):
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if any(bad in line.lower() for bad in ["downloaded from", "wiley", "terms and conditions", "doi", "online library"]):
            continue
        line = line.strip("- ")
        if len(line.strip()) > 10:
            cleaned.append(line)
    return "\n".join(cleaned)


def analyser_article(source, section="all", min_confidence=0.6):
    from datetime import datetime

    # 👉 Détection brute de texte
    if isinstance(source, str) and len(source.split()) > 10 and not os.path.exists(source) and not source.startswith("10."):
        resolved = source  # Texte brut
        doi = None
        crossref_metadata = {}
    else:
        resolved = load_source(source)
        doi = source if source.startswith("10.") else None
        crossref_metadata = enrich_doi_with_crossref(doi) if doi else {}

    if resolved is None:
        raise ValueError(f"Impossible de charger la source : {source}")

    if isinstance(resolved, str) and os.path.exists(resolved):
        raw_text = parse_pdf(resolved)
    else:
        raw_text = resolved

    if not raw_text.strip():
        raise ValueError("Texte vide extrait")

    full_text = clean_text(raw_text)
    lang = detect_language(full_text)
    sections = segment_sections(full_text, lang=lang)

    if section.lower() != "all":
        if section not in sections or not sections[section].strip():
            print(f"⚠️ Section '{section}' non trouvée ou vide, fallback automatique sur 'all'")
            text_to_analyze = "\n".join(sections.values())
        else:
            text_to_analyze = sections[section]
    else:
        text_to_analyze = "\n".join(sections.values())

    extractor, _, contextualiser, tracer, supervisor, citation_detector = initialize_agents()
    classifier = ClassificationAgent(confidence_threshold=min_confidence)

    results = run_pipeline(text_to_analyze, extractor, classifier, contextualiser, tracer, supervisor)

    for res in results:
        if isinstance(res["source"], str) and "doi.org/" in res["source"]:
            metadata = enrich_doi_with_crossref(res["source"])
            if metadata:
                res["source_metadata"] = metadata

    # 🔄 Extraction titre / auteurs depuis CrossRef si possible
    titre = crossref_metadata.get("title", [""])[0] if crossref_metadata else sections.get("titre", "")
    auteurs_list = crossref_metadata.get("author", []) if crossref_metadata else []
    auteurs = "; ".join([f"{a.get('given', '')} {a.get('family', '')}".strip() for a in auteurs_list]) if auteurs_list else "Inconnu"

    return {
        "titre": titre or "Titre inconnu",
        "auteurs": auteurs or "Inconnu",
        "doi": doi,
        "texte_source": full_text,
        "section_analysee": section,
        "sections": list(sections.keys()),
        "citations": results,
        "date_analyse": datetime.utcnow()
    }
