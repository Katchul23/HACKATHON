# main.py

import os
import json
import argparse
import requests
from pathlib import Path
from urllib.parse import urlparse
from colorama import Fore, init

from crew.crew_setup import initialize_agents
from crew.task_pipeline import run_pipeline
from utils.pdf_parser import parse_pdf
from utils.section_splitter import split_sections
from utils.lang_detector import detect_language
from agents.trace_agent import enrich_doi_with_crossref
from agents.classification_agent import ClassificationAgent  # <-- Import direct ici

init(autoreset=True)

def resolve_pdf_source(source):
    if source.lower().startswith("http"):
        response = requests.get(source)
        if response.status_code == 200 and 'application/pdf' in response.headers.get("Content-Type", ""):
            filename = os.path.basename(urlparse(source).path)
            local_path = f"data/input/{filename}"
            with open(local_path, "wb") as f:
                f.write(response.content)
            return local_path
        else:
            print(f"{Fore.RED}❌ Lien invalide ou non PDF : {source}")
            return None
    elif source.startswith("10."):
        doi_url = f"https://doi.org/{source}"
        print(f"{Fore.YELLOW}🔗 Redirection via DOI : {doi_url}")
        return resolve_pdf_source(doi_url)
    elif os.path.exists(source):
        return source
    else:
        print(f"{Fore.RED}❌ Source inconnue ou fichier introuvable : {source}")
        return None

def clean_text(text):
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if any(bad in line.lower() for bad in [
            "downloaded from", "wiley", "terms and conditions", "doi", "online library"
        ]):
            continue
        line = line.strip("- ")
        if len(line.strip()) > 10:
            cleaned.append(line)
    return "\n".join(cleaned)

def main():
    parser = argparse.ArgumentParser(description="Analyse automatique des citations de données.")
    parser.add_argument("--source", required=True, help="Chemin local, DOI ou URL vers un PDF")
    parser.add_argument("--min-confidence", type=float, default=0.6,
                        help="Seuil minimal de confiance pour classifier avec le modèle (0.0–1.0)")
    args = parser.parse_args()

    pdf_path = resolve_pdf_source(args.source)
    if not pdf_path or not os.path.exists(pdf_path):
        print(f"{Fore.RED}❌ Impossible d’accéder au PDF.")
        return

    print(f"{Fore.CYAN}📄 Extraction du texte depuis : {pdf_path}")
    raw_text = parse_pdf(pdf_path)

    if not raw_text.strip():
        print(f"{Fore.RED}❌ Aucun texte trouvé dans le PDF.")
        return

    full_text = clean_text(raw_text)

    print(f"{Fore.CYAN}🌍 Détection de la langue du texte...")
    lang = detect_language(full_text)
    print(f"{Fore.YELLOW}🔤 Langue détectée : {lang}")

    print(f"{Fore.CYAN}✂️  Découpage du texte en sections...")
    sections = split_sections(full_text, lang=lang)
    text_to_analyze = sections.get("méthodologie", "") or full_text

    print(f"{Fore.CYAN}🤖 Initialisation des agents CrewAI...")
    extractor, _, contextualiser, tracer, supervisor = initialize_agents()

    # Remplacement du classifier avec un seuil personnalisé
    classifier = ClassificationAgent(confidence_threshold=args.min_confidence)

    print(f"{Fore.CYAN}⚙️  Lancement de l’analyse...")
    results = run_pipeline(text_to_analyze, extractor, classifier, contextualiser, tracer, supervisor)

    for res in results:
        if isinstance(res["source"], str) and "doi.org/" in res["source"]:
            metadata = enrich_doi_with_crossref(res["source"])
            if metadata:
                res["source_metadata"] = metadata

    input_name = Path(pdf_path).stem
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)

    output_json = f"{output_dir}/{input_name}_results.json"
    output_md = f"{output_dir}/{input_name}_results.md"
    output_js = f"{output_dir}/{input_name}_results.js"

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    md_lines = [f"# Résultats de l’analyse : {input_name}\n"]
    js_data = {}
    for res in results:
        md_lines.append(f"## Phrase {res['phrase_index']}")
        md_lines.append(f"- **Texte** : {res['citation_text']}")
        md_lines.append(f"- **Type de données** : `{res['type_de_donnee']}`")
        md_lines.append(f"- **Contexte** : {res['contexte']}")
        md_lines.append(f"- **Source** : {res['source']}")
        if "source_metadata" in res:
            meta = res["source_metadata"]
            md_lines.append(f"  - **Titre** : {meta.get('titre', '')}")
            md_lines.append(f"  - **Auteurs** : {', '.join(meta.get('auteurs', []))}")
            md_lines.append(f"  - **Journal** : {meta.get('journal', '')}")
            md_lines.append(f"  - **Année** : {meta.get('annee', '')}")
            md_lines.append(f"  - **Éditeur** : {meta.get('editeur', '')}")
        md_lines.append("")

        js_data[res['phrase_index']] = {
            "citation_text": res["citation_text"],
            "type": res["type_de_donnee"],
            "context": res["contexte"],
            "source": res["source"],
            "source_metadata": res.get("source_metadata", {})
        }

    with open(output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    with open(output_js, "w", encoding="utf-8") as f:
        f.write("const dataCitations = ")
        json.dump(js_data, f, indent=2, ensure_ascii=False)
        f.write(";")

    print(f"{Fore.GREEN}📁 Résultats enregistrés dans : {output_json}")
    print(f"{Fore.GREEN}📝 Export Markdown : {output_md}")
    print(f"{Fore.GREEN}🧠 Export JavaScript : {output_js}")


if __name__ == "__main__":
    main()
