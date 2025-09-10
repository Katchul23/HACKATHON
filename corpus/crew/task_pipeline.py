from corpus.utils.lang_detector import detect_language
from corpus.utils.sentence_splitter import split_sentences

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
    print(f"🌍 Langue détectée : {lang}")

    # Étape 1 : extraction ciblée avec NER
    ner_mentions = extractor.extract_data_mentions(text)

    extracted_mentions = []
    if ner_mentions:
        print(f"🔎 {len(ner_mentions)} mentions extraites par NER.")
        for mention in ner_mentions:
            extracted_mentions.append({
                "index": -1,  # Pas d’indice de phrase
                "text": mention.get("text", "").strip(),
                "section": mention.get("section", None)
            })
    else:
        print("⚠️ Aucune mention détectée via NER. Fallback vers découpage phrase par phrase...")
        sentences = split_sentences(text, lang=lang)
        for idx, sentence in enumerate(sentences):
            if len(sentence.strip()) > 10:
                extracted_mentions.append({
                    "index": idx,
                    "text": sentence.strip(),
                    "section": None
                })

    print(f"📚 {len(extracted_mentions)} éléments envoyés pour classification.")
    
    # Étape 2 : délégation à l’agent superviseur
    results = supervisor.review_results(extracted_mentions, classifier, contextualiser, tracer)
    return results
