# File: services/autonomous_agent.py
import os
from pathlib import Path
import sys
from pathlib import Path
from datetime import datetime
from app.models.article import Article
from app.models.citation import Citation
from corpus.agents.trace_agent import enrich_doi_with_crossref
from corpus.agents.classification_agent import ClassificationAgent
from corpus.crew.crew_setup import initialize_agents
from corpus.crew.task_pipeline import run_pipeline
from corpus.utils.load_source import load_source
from corpus.utils.pdf_parser import parse_pdf
from corpus.utils.section_splitter import segment_sections
from corpus.utils.lang_detector import detect_language

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


def autonomous_analysis(source: str, db, section="all", min_confidence=0.6):
    # 1. Charger source (DOI, URL, fichier, texte brut)
    resolved = load_source(source)
    if resolved is None:
        raise ValueError("❌ Source introuvable ou vide")

    # 2. PDF ou texte ?
    raw_text = parse_pdf(resolved) if isinstance(resolved, str) and os.path.exists(resolved) else resolved
    if not raw_text.strip():
        raise ValueError("❌ Texte vide")

    # 3. Nettoyage et décodage
    full_text = clean_text(raw_text)
    lang = detect_language(full_text)
    sections = segment_sections(full_text, lang=lang)

    text_to_analyze = "\n".join(sections.values()) if section == "all" else sections.get(section, "")

    # 4. Initialisation des agents CrewAI
    extractor, _, contextualiser, tracer, supervisor, citation_detector = initialize_agents()
    classifier = ClassificationAgent(confidence_threshold=min_confidence)

    # 5. Lancer le pipeline IA
    results = run_pipeline(text_to_analyze, extractor, classifier, contextualiser, tracer, supervisor)

    # 6. Enrichir metadata DOI si possible
    doi = source if source.startswith("10.") else None
    metadata = enrich_doi_with_crossref(doi) if doi else {}

    # 7. Sauvegarde article
    article = Article(
        titre=metadata.get("title", [""])[0] if metadata else sections.get("titre", "Titre inconnu"),
        doi=doi,
        auteurs="; ".join(f"{a.get('given', '')} {a.get('family', '')}".strip() for a in metadata.get("author", [])) if metadata else "Inconnu",
        texte_source=full_text,
        section_analysee=section,
        date_analyse=datetime.utcnow()
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    # 8. Sauvegarde citations
    citations = []
    for c in results:
        citation = Citation(
            article_id=article.id,
            texte=c.get("citation_text") or c.get("contexte") or "[non précisé]",
            type_de_donnee=c.get("type_de_donnee", "inconnu"),
            contexte=c.get("contexte", ""),
            source=c.get("source", ""),
            source_metadata=c.get("source_metadata") or None
        )
        db.add(citation)
        db.flush()
        db.refresh(citation)
        citations.append(citation)

    db.commit()

    return article, citations
