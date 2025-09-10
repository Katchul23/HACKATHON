# app/schemas/article.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.citation import CitationOut


# ✅ Schéma utilisé pour la création (POST /articles/)
class ArticleCreate(BaseModel):
    source: str  # DOI, URL, chemin PDF local, ou texte brut
    auteurs: Optional[str] = None
    section_analysee: Optional[str] = "all"


# ✅ Schéma utilisé pour la réponse complète (GET /articles/)
class ArticleOut(BaseModel):
    id: int
    titre: Optional[str]
    doi: Optional[str]
    auteurs: Optional[str]
    section_analysee: Optional[str]
    texte_source: Optional[str]
    date_analyse: datetime
    citations: List[CitationOut] = []

    class Config:
        from_attributes = True
