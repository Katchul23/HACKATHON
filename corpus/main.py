import os
import json
import argparse
import requests
from pathlib import Path
from urllib.parse import urlparse, quote
from colorama import Fore, init

from crew.crew_setup import initialize_agents
from crew.task_pipeline import run_pipeline
from utils.pdf_parser import parse_pdf
from utils.section_splitter import segment_sections
from utils.lang_detector import detect_language
from utils.load_source import load_source
from utils.exporter import export_results
from agents.trace_agent import enrich_doi_with_crossref
from agents.classification_agent import ClassificationAgent

init(autoreset=True)

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

def main():
    parser = argparse.ArgumentParser(description="Analyse automatique des citations de données.")
    parser.add_argument("--source", required=True, help="Chemin local, DOI ou URL vers un PDF ou une ressource textuelle")
    parser.add_argument("--min-confidence", type=float, default=0.6,
                        help="Seuil minimal de confiance pour classifier (entre 0.0 et 1.0)")
    parser.add_argument("--section", default="all",
                        help="Section à analyser (ex : méthodologie, résultats, conclusion, all)")
    args = parser.parse_args()

    resolved = load_source(args.source)
    if resolved is None:
        print(f"{Fore.RED}❌ Impossible d'accéder au contenu.")
        return

    if isinstance(resolved, str) and os.path.exists(resolved):
        print(f"{Fore.CYAN}📄 Extraction du texte depuis : {resolved}")
        raw_text = parse_pdf(resolved)
        input_name = Path(resolved).stem
    else:
        print(f"{Fore.CYAN}📄 Utilisation directe du texte récupéré (CrossRef ou Dryad)")
        raw_text = resolved
        input_name = args.source.replace("/", "_")[:50]

    if not raw_text.strip():
        print(f"{Fore.RED}❌ Aucun texte trouvé.")
        return

    full_text = clean_text(raw_text)
    print(f"{Fore.CYAN}🌍 Détection de la langue...")
    lang = detect_language(full_text)
    print(f"{Fore.YELLOW}🌟 Langue détectée : {lang}")

    print(f"{Fore.CYAN}✂️ Découpage du texte en sections...")
    sections = segment_sections(full_text, lang=lang)
    section = args.section.lower()

    if section != "all":
        if section not in sections:
            print(f"{Fore.RED}❌ Section inconnue : {args.section}")
            print(f"{Fore.YELLOW}👉 Sections disponibles : {list(sections.keys())}")
            return
        elif not sections[section].strip():
            print(f"{Fore.RED}❌ La section '{section}' existe mais est vide.")
            return
        text_to_analyze = sections[section]
        print(f"{Fore.BLUE}🔎 Analyse de la section : {section}")
    else:
        text_to_analyze = "\n".join(sections.values())
        print(f"{Fore.BLUE}🔎 Analyse de l’ensemble du texte")

    print(f"{Fore.CYAN}🤖 Initialisation des agents CrewAI...")
    extractor, _, contextualiser, tracer, supervisor, citation_detector = initialize_agents()
    classifier = ClassificationAgent(confidence_threshold=args.min_confidence)

    print(f"{Fore.CYAN}⚙️ Lancement de l'analyse...")
    results = run_pipeline(text_to_analyze, extractor, classifier, contextualiser, tracer, supervisor)

    for res in results:
        if isinstance(res["source"], str) and "doi.org/" in res["source"]:
            metadata = enrich_doi_with_crossref(res["source"])
            if metadata:
                res["source_metadata"] = metadata

    citation_results = citation_detector.detect_citations(full_text)

    export_results(results, citation_results, input_name)

if __name__ == "__main__":
    main()
