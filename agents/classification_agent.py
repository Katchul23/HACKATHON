# Placeholder for classification_agent.py
from models.classify_model import DataClassifierModel

class ClassificationAgent:
    def __init__(self, confidence_threshold=0.6):
        self.name = "ClassificationAgent"
        self.model = DataClassifierModel(model_path="models/saved/final_classifier_50k.joblib")
        self.confidence_threshold = confidence_threshold

        # 🔹 Mots-clés français - Primaire
        self.primary_keywords = [
            "notre étude", "nous avons collecté", "données recueillies", "enquête menée",
            "mesures effectuées", "observations réalisées", "données produites",
            "collecte sur le terrain", "questionnaire administré", "échantillons prélevés",
            "campagne de terrain", "logiciel propriétaire utilisé", "capteur", "enquête locale"
        ]

        # 🔹 Mots-clés français - Secondaire
        self.secondary_keywords = [
            "publiées par", "source", "rapport", "archives", "base de données existante",
            "données issues de", "provenant de", "données téléchargées", "reprise de données",
            "archives historiques", "données antérieures", "modèles existants", "rapports ministériels"
        ]

        # 🔹 Mots-clés anglais - Primaire
        self.primary_keywords += [
            "we collected", "data we gathered", "in our study", "experiment conducted",
            "data were obtained", "measured values", "survey conducted", "data were generated",
            "data collection", "observed data", "field campaign", "questionnaire administered",
            "sensor data", "sampling", "software used to process"
        ]

        # 🔹 Mots-clés anglais - Secondaire
        self.secondary_keywords += [
            "data from", "according to", "dataset downloaded", "source:", 
            "based on report", "archival data", "data retrieved", "existing database",
            "data reused", "cited from", "prior models", "historical archives",
            "previous studies", "secondary sources", "did not involve new data"
        ]

    def classify(self, citation_text):
        """
        Classifie une phrase comme citation de données primaires, secondaires ou inconnues.
        Combine approche heuristique + modèle supervisé avec seuil de confiance.

        Args:
            citation_text (str): Phrase contenant une citation de données.

        Returns:
            str: "primaire", "secondaire" ou "inconnu"
        """
        text = citation_text.lower()

        # 🔍 Étape 1 : Heuristique
        if any(keyword in text for keyword in self.primary_keywords):
            return "primaire"
        elif any(keyword in text for keyword in self.secondary_keywords):
            return "secondaire"

        # 🧠 Étape 2 : Modèle supervisé avec seuil
        try:
            label, confidence = self.model.predict_with_confidence(citation_text)
            if confidence >= self.confidence_threshold:
                return label
            else:
                return "inconnu"
        except Exception as e:
            print(f"[ClassificationAgent] ⚠️ Erreur de prédiction : {e}")
            return "inconnu"

