# Placeholder for task_pipeline.py
# task_pipeline.py

from utils.lang_detector import detect_language
from utils.sentence_splitter import split_sentences

def run_pipeline(text, extractor, classifier, contextualiser, tracer, supervisor):
    """
    Exécute le pipeline complet d'analyse d'un texte scientifique pour détecter, classer
    et contextualiser les citations de données.

    Args:
        text (str): Texte intégral de l’article scientifique.
        extractor (ExtractionAgent): Agent chargé d'extraire les mentions de données.
        classifier (ClassificationAgent): Agent chargé de déterminer le type de données.
        contextualiser (ContextualisationAgent): Agent chargé de résumer le contexte d’usage.
        tracer (TraceAgent): Agent chargé d’identifier la source des données.
        supervisor (SupervisorAgent): Agent coordonnant et validant l’ensemble.

    Returns:
        list[dict]: Liste des objets contenant les résultats consolidés par mention de données.
    """

    lang = detect_language(text)
    sentences = split_sentences(text, lang=lang)

    extracted_mentions = []
    for idx, sentence in enumerate(sentences):
        if not sentence.strip():
            continue

        mentions = extractor.extract_data_mentions(sentence)
        for citation in mentions:
            extracted_mentions.append({
                "index": idx,
                "text": citation["text"] if isinstance(citation, dict) and "text" in citation else citation
            })

    # 💡 Délégation de la classification + contextualisation + traçage au superviseur
    results = supervisor.review_results(extracted_mentions, classifier, contextualiser, tracer)
    return results

