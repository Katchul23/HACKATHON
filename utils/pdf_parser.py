# Placeholder for pdf_parser.py
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
        #print("************** TEXTE PDF***************\n", text)
        return text
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte : {e}")
        return ""
