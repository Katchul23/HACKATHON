# pre_process_agent.py
import os
import mimetypes
import textract
import html2text
import fitz  # PyMuPDF
from bs4 import BeautifulSoup


def detect_format(file_path_or_content):
    """
    Détecte le format du fichier local ou du contenu brut (PDF, HTML, texte, doc).
    """
    if isinstance(file_path_or_content, str) and os.path.exists(file_path_or_content):
        mime, _ = mimetypes.guess_type(file_path_or_content)
        ext = os.path.splitext(file_path_or_content)[-1].lower()
        if mime:
            if mime == "application/pdf":
                return "pdf"
            elif mime.startswith("text/html") or ext in [".html", ".htm"]:
                return "html"
            elif mime.startswith("text") or ext in [".txt", ".md"]:
                return "text"
            elif ext in [".docx", ".doc", ".odt"]:
                return "doc"
        return "unknown"
    else:
        # Cas où le contenu est une chaîne texte directe
        if "<html" in file_path_or_content.lower():
            return "html"
        return "text"


def extract_text(source, format_hint=None):
    """
    Extrait le texte brut à partir d’un fichier ou d’un contenu brut selon le format détecté.

    Args:
        source (str): Chemin du fichier ou contenu brut.
        format_hint (str | None): Type de fichier si déjà connu ("pdf", "html", etc.)

    Returns:
        str: Texte brut extrait ou vide si erreur.
    """
    detected = format_hint or detect_format(source)

    # 🔍 Extraction depuis un fichier local
    if isinstance(source, str) and os.path.exists(source):
        try:
            if detected == "pdf":
                text = ""
                with fitz.open(source) as doc:
                    for page in doc:
                        text += page.get_text()
                return text.strip()
            elif detected == "doc":
                return textract.process(source).decode("utf-8").strip()
            elif detected == "text":
                with open(source, encoding="utf-8", errors="ignore") as f:
                    return f.read().strip()
            elif detected == "html":
                with open(source, encoding="utf-8", errors="ignore") as f:
                    html = f.read()
                return html2text.html2text(html).strip()
        except Exception as e:
            print(f"[ERREUR] Impossible d’extraire depuis le fichier ({detected}) : {e}")
            return ""

    # 🧾 Extraction depuis un contenu brut
    elif isinstance(source, str):
        try:
            if detected == "html":
                return html2text.html2text(source).strip()
            return source.strip().replace("\u00a0", " ")  # nettoyage basique
        except Exception as e:
            print(f"[ERREUR] Impossible de nettoyer le contenu ({detected}) : {e}")
            return ""

    return ""
