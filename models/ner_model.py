# Placeholder for ner_model.py
import spacy

class NERModel:
    def __init__(self, model_name="en_core_web_sm"):
        """
        Initialise un modèle SpaCy pré-entraîné.
        Args:
            model_name (str): Nom du modèle à charger (par défaut: anglais standard)
        """
        self.nlp = spacy.load(model_name)

    def extract_entities(self, text):
        """
        Extrait les entités nommées du texte, utiles pour contextualiser les données.

        Args:
            text (str): Texte à analyser

        Returns:
            list[dict]: Liste d'entités avec leur type
        """
        doc = self.nlp(text)
        results = []

        for ent in doc.ents:
            results.append({
                "text": ent.text,
                "label": ent.label_
            })

        return results
