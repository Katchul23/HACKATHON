# app/schemas/citation.py
from pydantic import BaseModel
from typing import Optional, List

class SourceMetadata(BaseModel):
    titre: Optional[str]
    auteurs: Optional[List[str]]
    journal: Optional[str]
    annee: Optional[str]
    editeur: Optional[str]

class CitationOut(BaseModel):
    id: int
    article_id: int
    texte: str
    type_de_donnee: Optional[str]
    contexte: Optional[str]
    source: Optional[str]
    source_metadata: Optional[SourceMetadata]

    class Config:
        from_attributes = True


