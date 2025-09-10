# pdf_parser.py — Extraction texte brut depuis PDF
from pdfminer.high_level import extract_text


def parse_pdf(file_path):
    """
    Extrait le texte brut d’un fichier PDF.

    Args:
        file_path (str): Chemin du fichier PDF à analyser.

    Returns:
        str: Texte extrait.
    """
    try:
        text = extract_text(file_path)
        if not text.strip():
            print("⚠️ Le texte extrait est vide ou peu lisible.")
        else:
            print(f"✅ Texte extrait depuis : {file_path} (taille : {len(text)} caractères)")
        return text
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction du texte : {e}")
        return ""
