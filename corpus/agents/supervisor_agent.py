# supervisor_agent.py amélioré
import os
import json

class SupervisorAgent:
    def __init__(self):
        self.name = "SupervisorAgent"
        self.rejections = []
        self.rejection_path = "data/output/rejected_predictions.md"
        self.json_output_path = "data/output/final_validated_results.json"
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
            extracted_mentions (list[dict]): Liste des mentions extraites avec index, texte, section, etc.
            classifier, contextualiser, tracer: Agents spécialisés.

        Returns:
            list[dict]: Résultats consolidés et filtrés.
        """
        results = []
        seen_texts = set()

        for mention in extracted_mentions:
            index = mention.get("index")
            text = mention.get("text", "").strip()
            section = mention.get("section", None)

            if not self.is_valid(text):
                self._log_rejection(index, text, "Phrase trop courte ou bruitée")
                continue
            if self.is_duplicate(text, seen_texts):
                self._log_rejection(index, text, "Doublon détecté")
                continue

            try:
                data_type = classifier.classify(text, section_name=section)
                if data_type == "inconnu":
                    self._log_rejection(index, text, "Classification incertaine")
                    continue

                context = contextualiser.summarize_context(text)
                source = tracer.trace_source(text)

                result = {
                    "phrase_index": index,
                    "citation_text": text,
                    "type_de_donnee": data_type,
                    "contexte": context,
                    "source": source
                }
                if section:
                    result["section"] = section

                results.append(result)
                print(f"✅ Phrase {index} validée : {data_type} | section={section}")

            except Exception as e:
                self._log_rejection(index, text, f"Erreur d'analyse : {str(e)}")
                continue

        self._save_rejections()
        self._save_json(results)
        return results

    def _log_rejection(self, index, text, reason):
        print(f"⛔️ Rejet phrase {index} : {reason}")
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

    def _save_json(self, results):
        try:
            with open(self.json_output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 Résultats sauvegardés dans {self.json_output_path}")
        except Exception as e:
            print(f"⚠️ Erreur de sauvegarde JSON : {e}")
