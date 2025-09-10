import os
import json
from pathlib import Path

def export_results(results, citation_results, input_name, output_dir="data/output"):
    os.makedirs(output_dir, exist_ok=True)

    output_json = f"{output_dir}/{input_name}_results.json"
    output_md = f"{output_dir}/{input_name}_results.md"
    output_js = f"{output_dir}/{input_name}_results.js"
    output_cit = f"{output_dir}/{input_name}_citations.json"

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(output_cit, "w", encoding="utf-8") as f:
        json.dump(citation_results, f, indent=2, ensure_ascii=False)

    md_lines = [f"# Résultats de l'analyse : {input_name}\n"]
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

    print(f"\U0001F4C1 Résultats enregistrés dans : {output_json}")
    print(f"\U0001F4CC Citations globales extraites dans : {output_cit}")
    print(f"\U0001F4D1 Export Markdown : {output_md}")
    print(f"🧐 Export JavaScript : {output_js}")
