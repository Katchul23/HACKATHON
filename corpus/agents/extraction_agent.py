import re
import spacy
import fitz  # PyMuPDF
from corpus.utils.section_splitter import segment_sections

class ExtractionAgent:
    def __init__(self):
        self.name = "ExtractionAgent"
        model_candidates = [
            "en_ner_bionlp13cg_md",
            "en_core_sci_sm",
            "en_core_web_sm"
        ]
        for model in model_candidates:
            try:
                self.nlp = spacy.load(model)
                print(f"✅ Modèle SpaCy chargé : {model}")
                break
            except Exception as e:
                print(f"⚠️ Impossible de charger {model} : {e}")
        else:
            raise RuntimeError("❌ Aucun modèle SpaCy valide n'a pu être chargé.")

    def contains_numeric_pattern(self, text):
        pattern = r'\b\d+(\.\d+)?\s?(°C|samples?|experiments?|measurements?|atm|kg|g|mm|cm|%)'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def extract_data_mentions(self, text):
        """
        Repère les phrases contenant des références à des données,
        avec un modèle NER contextuel et séparation par section.

        Args:
            text (str): Texte complet de l'article scientifique.

        Returns:
            list[dict]: Liste des citations avec contexte et section.
        """
        results = []
        sections = segment_sections(text)

        DATA_LABELS = {"data", "dataset", "source", "value", "measurement", "quantity"}

        for section_name, section_text in sections.items():
            if len(section_text.strip()) < 50:
                continue
            doc = self.nlp(section_text)
            for ent in doc.ents:
                print(f"🔍 {ent.text} [{ent.label_}] dans : {ent.sent.text.strip()[:200]}...")
                if ent.label_.lower() in DATA_LABELS:
                    results.append({
                        "section": section_name,
                        "text": ent.sent.text.strip(),
                        "span": ent.text,
                        "label": ent.label_
                    })

            # 🔁 fallback regex sémantique simple (si NER échoue)
            for sent in section_text.split("."):
                if self.contains_numeric_pattern(sent):
                    results.append({
                        "section": section_name,
                        "text": sent.strip(),
                        "span": "regex",  # ou mettre l'extrait exact
                        "label": "pattern"
                    })

        return results

    def extract_text_from_pdf(self, file_path):
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
