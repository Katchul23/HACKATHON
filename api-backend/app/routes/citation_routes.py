from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.models.citation import Citation
from app.schemas.citation import CitationOut

router = APIRouter(prefix="/citations", tags=["Citations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{id}", response_model=CitationOut)
def get_citation(id: int, db: Session = Depends(get_db)):
    citation = db.query(Citation).filter(Citation.id == id).first()
    if not citation:
        raise HTTPException(status_code=404, detail="Citation non trouvée")
    return citation

@router.get("/", response_model=List[CitationOut])
def list_citations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Liste paginée des citations.
    Exemple : /citations?skip=0&limit=50
    """
    return db.query(Citation).offset(skip).limit(limit).all()

@router.get("/article/{article_id}", response_model=List[CitationOut])
def get_citations_by_article(article_id: int, db: Session = Depends(get_db)):
    """
    Toutes les citations associées à un article.
    """
    return db.query(Citation).filter(Citation.article_id == article_id).all()
