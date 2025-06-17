# Placeholder for contextualisation_agent.py
class ContextualisationAgent:
    def __init__(self):
        self.name = "ContextualisationAgent"

    def summarize_context(self, citation_text):
        """
        Génère un résumé simple du contexte d’usage de la citation de données.

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

        # 🔸 Par défaut : tronque proprement la phrase comme contexte
        clean_preview = citation_text.strip().replace("\n", " ").replace("  ", " ")
        if len(clean_preview) > 100:
            clean_preview = clean_preview[:97] + "..."
        return f"Contexte d’utilisation : {clean_preview}"
