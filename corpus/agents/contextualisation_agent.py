# contextualisation_agent.py amélioré avec modèle LLM optionnel
from transformers import pipeline

class ContextualisationAgent:
    def __init__(self, use_llm=False):
        self.name = "ContextualisationAgent"
        self.use_llm = use_llm
        self.summarizer = None

        if self.use_llm:
            try:
                self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
                print("[ContextualisationAgent] ✅ Modèle de résumé chargé.")
            except Exception as e:
                print(f"[ContextualisationAgent] ⚠️ Erreur de chargement LLM : {e}")
                self.use_llm = False

    def summarize_context(self, citation_text):
        """
        Génère un résumé simple ou LLM du contexte d’usage de la citation de données.

        Args:
            citation_text (str): Phrase contenant une citation de données.

        Returns:
            str: Résumé du contexte d'utilisation.
        """
        text = citation_text.lower()

        # 🔹 Heuristique multilingue
        if "pour analyser" in text or "to analyze" in text:
            return "Les données ont été utilisées à des fins d'analyse."
        elif "afin de comprendre" in text or "to understand" in text:
            return "Les données ont servi à mieux comprendre un phénomène."
        elif "dans le cadre de" in text or "as part of" in text:
            return "Les données ont été mobilisées dans un cadre spécifique d'étude."
        elif "utilisées pour" in text or "used for" in text or "used to" in text:
            return "Utilisation fonctionnelle des données identifiée."
        elif "comparées à" in text or "compared to" in text:
            return "Les données ont été utilisées pour des comparaisons."
        elif "collectées afin de" in text or "collected to" in text:
            return "Données collectées dans un objectif défini."
        elif "dans cette étude" in text or "in this study" in text:
            return "Les données ont été mobilisées dans le cadre de l'étude actuelle."

        # 🔸 Option LLM
        if self.use_llm and self.summarizer:
            try:
                summary = self.summarizer(citation_text, max_length=50, min_length=10, do_sample=False)
                return summary[0]['summary_text']
            except Exception as e:
                print(f"[ContextualisationAgent] Erreur LLM fallback : {e}")

        # 🔸 Fallback par défaut : tronque la phrase
        clean_preview = citation_text.strip().replace("\n", " ").replace("  ", " ")
        if len(clean_preview) > 100:
            clean_preview = clean_preview[:97] + "..."
        return f"Contexte d’utilisation : {clean_preview}"
