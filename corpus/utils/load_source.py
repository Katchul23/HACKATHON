# utils/load_source.py

import os
import requests
from urllib.parse import urlparse, quote
from colorama import Fore
from corpus.agents.pre_process_agent import detect_format, extract_text


def load_source(source):
    """
    Charge la source d'entrée (fichier local, URL, DOI) et retourne soit :
    - le chemin vers un fichier PDF local
    - ou un texte brut si disponible (CrossRef, Dryad, etc.)

    Returns:
        str | None: chemin vers fichier PDF ou texte brut, sinon None
    """
    if source.lower().startswith("http"):
        try:
            response = requests.get(source)
            if response.status_code == 200 and 'application/pdf' in response.headers.get("Content-Type", ""):
                filename = os.path.basename(urlparse(source).path)
                local_path = f"corpus/data/input/{filename}"
                os.makedirs(os.path.dirname(local_path), exist_ok=True)  # ✅ Crée le dossier si besoin
                with open(local_path, "wb") as f:
                    f.write(response.content)
                return local_path
            else:
                print(f"{Fore.RED}❌ Lien invalide ou non PDF : {source}")
                return None
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la récupération de l'URL : {e}")
            return None

    elif source.startswith("10."):
        # 1. Dryad
        if source.startswith("10.5061/"):
            doi_encoded = quote(f"doi:{source}")
            dryad_url = f"https://datadryad.org/api/v2/datasets/{doi_encoded}"
            print(f"{Fore.YELLOW}🔍 Récupération via API Dryad : {dryad_url}")
            try:
                response = requests.get(dryad_url)
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    attributes = data.get("attributes", {})
                    title = attributes.get("title", "")
                    abstract = attributes.get("abstract", "")
                    authors = ", ".join([a.get("name", "") for a in attributes.get("authors", [])])
                    full_text = f"{title}\n{authors}\n{abstract}"
                    print(f"{Fore.CYAN}🧾 Texte récupéré depuis Dryad")
                    return full_text
                else:
                    print(f"{Fore.RED}❌ Échec récupération Dryad (code {response.status_code})")
            except Exception as e:
                print(f"{Fore.RED}❌ Erreur Dryad : {e}")

        # 2. CrossRef
        doi_url = f"https://api.crossref.org/works/{source}"
        print(f"{Fore.YELLOW}🔍 Récupération via CrossRef API : {doi_url}")
        try:
            response = requests.get(doi_url)
            if response.status_code == 200:
                metadata = response.json().get("message", {})
                abstract = metadata.get("abstract", "")
                title = metadata.get("title", [""])[0]
                authors = ", ".join([a.get("family", "") for a in metadata.get("author", [])])
                full_text = f"{title}\n{authors}\n{abstract}"
                print(f"{Fore.CYAN}🧾 Texte récupéré via CrossRef")
                return full_text
            else:
                print(f"{Fore.RED}❌ DOI introuvable sur CrossRef (code {response.status_code})")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur CrossRef : {e}")

        # 3. Redirection DOI -> PDF direct ?
        doi_url_pdf = f"https://doi.org/{source}"
        print(f"{Fore.YELLOW}🔗 Tentative via DOI direct : {doi_url_pdf}")
        try:
            response = requests.get(doi_url_pdf, allow_redirects=True)
            if response.status_code == 200 and 'application/pdf' in response.headers.get("Content-Type", ""):
                filename = f"{source.replace('/', '_')}.pdf"
                local_path = f"data/input/{filename}"
                with open(local_path, "wb") as f:
                    f.write(response.content)
                print(f"{Fore.CYAN}📄 PDF récupéré via redirection DOI")
                return local_path
            else:
                print(f"{Fore.RED}❌ Lien DOI direct ne pointe pas vers un PDF (code {response.status_code})")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du téléchargement via DOI : {e}")

        return None

    elif os.path.exists(source):
        # 🧠 Utilisation d’un extracteur intelligent pour fichiers locaux non PDF
        format_detected = detect_format(source)
        if format_detected == "pdf":
            return source
        else:
            print(f"{Fore.CYAN}🧪 Extraction de texte depuis un fichier {format_detected}")
            extracted = extract_text(source, filetype=format_detected)
            return extracted if extracted else None

    else:
        print(f"{Fore.RED}❌ Source inconnue ou fichier introuvable : {source}")
        return None
