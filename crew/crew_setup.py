# Placeholder for crew_setup.py
from agents.extraction_agent import ExtractionAgent
from agents.classification_agent import ClassificationAgent
from agents.contextualisation_agent import ContextualisationAgent
from agents.trace_agent import TraceAgent
from agents.supervisor_agent import SupervisorAgent

def initialize_agents():
    """
    Initialise tous les agents du système Multi-Agent.

    Returns:
        tuple: Instances des agents dans l'ordre (extractor, classifier, contextualiser, tracer, supervisor)
    """
    extractor = ExtractionAgent()
    classifier = ClassificationAgent()
    contextualiser = ContextualisationAgent()
    
    # ✅ Activer l'enrichissement Crossref ici
    tracer = TraceAgent(enrich_with_crossref=True)
    
    supervisor = SupervisorAgent()

    return extractor, classifier, contextualiser, tracer, supervisor


