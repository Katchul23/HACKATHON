# lang_detector.py

from langdetect import detect, DetectorFactory
DetectorFactory.seed = 42  # Pour rendre les résultats reproductibles

def detect_language(text):
    """
    Détecte la langue principale d’un texte donné.

    Args:
        text (str): Texte à analyser.

    Returns:
        str: Code de langue détecté ('fr', 'en', etc.)
    """
    try:
        return detect(text)
    except Exception as e:
        return f"Erreur: {str(e)}"