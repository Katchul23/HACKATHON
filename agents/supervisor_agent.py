# supervisor_agent.py

import os

class SupervisorAgent:
    def __init__(self):
        self.name = "SupervisorAgent"
        self.rejections = []
        self.rejection_path = "data/output/rejected_predictions.md"
        os.makedirs(os.path.dirname(self.rejection_path), exist_ok=True)

    def is_duplicate(self, citation, seen_texts):
        norm = citation.strip().lower()
        if norm in seen_texts:
            return True
        seen_texts.add(norm)
        return False

    def is_valid(self, citation):
        """
        Règles simples pour éliminer les fausses détections.
        - Ignore les citations très courtes ou bruitées.
        """
        return len(citation.strip()) >= 20 and any(c.isalpha() for c in citation)

    def review_results(self, extracted_mentions, classifier, contextualiser, tracer):
        """
        Orchestration : collecte les résultats de chaque agent, applique des règles de validation
        et enregistre les rejets.

        Args:
            extracted_mentions (list[dict]): Liste des mentions extraites avec index et texte.
            classifier, contextualiser, tracer: Agents spécialisés.

        Returns:
            list[dict]: Résultats consolidés et filtrés.
        """
        results = []
        seen_texts = set()

        for mention in extracted_mentions:
            index = mention.get("index")
            text = mention.get("text", "").strip()

            if not self.is_valid(text):
                self._log_rejection(index, text, "Phrase trop courte ou bruitée")
                continue
            if self.is_duplicate(text, seen_texts):
                self._log_rejection(index, text, "Doublon détecté")
                continue

            try:
                data_type = classifier.classify(text)
                if data_type == "inconnu":
                    self._log_rejection(index, text, "Classification incertaine")
                    continue

                context = contextualiser.summarize_context(text)
                source = tracer.trace_source(text)

                results.append({
                    "phrase_index": index,
                    "citation_text": text,
                    "type_de_donnee": data_type,
                    "contexte": context,
                    "source": source
                })
            except Exception as e:
                self._log_rejection(index, text, f"Erreur d'analyse : {str(e)}")
                continue

        self._save_rejections()
        return results

    def _log_rejection(self, index, text, reason):
        self.rejections.append({
            "index": index,
            "text": text,
            "raison": reason
        })

    def _save_rejections(self):
        if not self.rejections:
            return
        with open(self.rejection_path, "w", encoding="utf-8") as f:
            f.write("# 🛑 Prédictions rejetées\n\n")
            for r in self.rejections:
                f.write(f"## Phrase {r['index']}\n")
                f.write(f"- **Texte** : {r['text']}\n")
                f.write(f"- **Raison du rejet** : {r['raison']}\n\n")
