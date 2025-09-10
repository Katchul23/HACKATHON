# crew_setup.py — Initialisation des agents
from corpus.agents.extraction_agent import ExtractionAgent
from corpus.agents.classification_agent import ClassificationAgent
from corpus.agents.contextualisation_agent import ContextualisationAgent
from corpus.agents.trace_agent import TraceAgent
from corpus.agents.supervisor_agent import SupervisorAgent
from corpus.agents.citation_agent import CitationDetectionAgent

def initialize_agents(use_llm=False, enrich_crossref=True):
    """
    Initialise tous les agents du système Multi-Agent.

    Args:
        use_llm (bool): Active le résumé LLM pour le contextualiseur
        enrich_crossref (bool): Active l'enrichissement Crossref pour les sources

    Returns:
        tuple: Instances des agents dans l'ordre (extractor, classifier, contextualiser, tracer, supervisor)
    """
    extractor = ExtractionAgent()
    classifier = ClassificationAgent()
    contextualiser = ContextualisationAgent(use_llm=use_llm)
    tracer = TraceAgent(enrich_with_crossref=enrich_crossref)
    supervisor = SupervisorAgent()
    citation_detector = CitationDetectionAgent()

    return extractor, classifier, contextualiser, tracer, supervisor, citation_detector
