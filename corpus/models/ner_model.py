# ner_model.py — Extraction d'entités nommées avec SpaCy
import spacy

class NERModel:
    def __init__(self, model_name="en_core_web_sm"):
        """
        Initialise un modèle SpaCy pré-entraîné.
        Args:
            model_name (str): Nom du modèle à charger (par défaut: anglais standard)
        """
        try:
            self.nlp = spacy.load(model_name)
            print(f"✅ Modèle NER chargé : {model_name}")
        except Exception as e:
            print(f"❌ Erreur de chargement SpaCy : {e}")
            self.nlp = None

    def extract_entities(self, text, filter_labels=None):
        """
        Extrait les entités nommées du texte, utiles pour contextualiser les données.

        Args:
            text (str): Texte à analyser
            filter_labels (list[str] | None): Labels d'entités à extraire (ex: ["ORG", "DATE"])

        Returns:
            list[dict]: Liste d'entités avec leur type
        """
        if not self.nlp:
            return []

        doc = self.nlp(text)
        results = []

        for ent in doc.ents:
            if filter_labels and ent.label_ not in filter_labels:
                continue
            results.append({
                "text": ent.text,
                "label": ent.label_
            })

        return results
