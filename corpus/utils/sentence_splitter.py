# utils/sentence_splitter.py — Segmentation multilingue robuste
import re
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk.tokenize import sent_tokenize

# 📦 Vérifie que le tokenizer punkt est dispo
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def split_sentences(text, lang="fr"):
    """
    Segmente proprement un texte scientifique en phrases, en tenant compte de la langue.

    Args:
        text (str): Texte brut.
        lang (str): 'fr' ou 'en'.

    Returns:
        list[str]: Liste de phrases nettoyées.
    """
    custom_abbreviations = {"et al", "fig", "dr", "prof", "e.g", "i.e", "etc"}

    # 🧼 Nettoyage léger
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(?<=[a-zA-Z])-(?=[a-zA-Z])", "", text)  # supprime les césures de mots

    # 🔧 Configuration des abréviations
    punkt_params = PunktParameters()
    punkt_params.abbrev_types = custom_abbreviations
    tokenizer = PunktSentenceTokenizer(punkt_params)

    try:
        if lang == "fr":
            sentences = sent_tokenize(text, language="french")
        elif lang == "en":
            sentences = sent_tokenize(text, language="english")
        else:
            sentences = tokenizer.tokenize(text)
    except Exception:
        # Fallback naïf si NLTK échoue
        sentences = re.split(r"(?<=[.!?])\s+", text)

    return [s.strip() for s in sentences if len(s.strip()) > 10]
