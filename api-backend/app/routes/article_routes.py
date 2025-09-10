# app/routes/article_routes.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.config import SessionLocal
from app.models.article import Article
from app.models.citation import Citation
from app.schemas.article import ArticleCreate, ArticleOut
from app.schemas.citation import CitationOut

from app.services.analyse_service import analyser_article
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


# (plus tard) : from app.services.analyse_service import analyser_article

router = APIRouter(prefix="/articles", tags=["Articles"])

# 💡 Dependency pour ouvrir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# GET /articles/
@router.get("/", response_model=List[ArticleOut])
def list_articles(db: Session = Depends(get_db)):
    return db.query(Article).all()


# GET /articles/{id}
@router.get("/{id}", response_model=ArticleOut)
def get_article(id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article


# DELETE /articles/{id}
@router.delete("/{id}")
def delete_article(id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    db.delete(article)
    db.commit()
    return {"message": "✅ Article supprimé"}

# POST /articles/analyse (avec pipeline IA réel)
@router.post("/analyse", response_model=ArticleOut)
def analyse_article(payload: ArticleCreate, db: Session = Depends(get_db)):
    try:
        result = analyser_article(
            source=payload.source.strip(),
            section=payload.section_analysee or "all"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Erreur d'analyse : {str(e)}")

    doi = result.get("doi") or (payload.source if payload.source.startswith("10.") else None)

    # ✅ Vérifie si un article avec ce DOI existe déjà
    if doi:
        existing_article = db.query(Article).filter(Article.doi == doi).first()
        if existing_article:
            print(f"⚠️ Article déjà présent avec DOI {doi} → ID {existing_article.id}")
            return existing_article

    # Création nouvelle entrée Article
    article = Article(
        titre=result.get("titre", "Titre inconnu"),
        doi=doi,
        section_analysee=payload.section_analysee,
        texte_source=result.get("texte_source", "[non disponible]"),
        auteurs=result.get("auteurs", "Inconnu")
    )

    try:
        db.add(article)
        db.commit()
        db.refresh(article)

        # 🔁 Ajout des citations
        for i, c in enumerate(result.get("citations", [])):
            try:
                print(f"📌 Insertion citation #{i} → {c}")
                if not c.get("citation_text") and not c.get("contexte"):
                    print(f"⛔️ Citation #{i} ignorée : pas de contenu textuel")
                    continue

                citation = Citation(
                    article_id=article.id,
                    texte=c.get("citation_text") or c.get("contexte") or "[non précisé]",
                    type_de_donnee=c.get("type_de_donnee", "inconnu"),
                    contexte=c.get("contexte", ""),
                    source=c.get("source", ""),
                    source_metadata=c.get("source_metadata") or None
                )
                db.add(citation)
                db.flush()
                db.refresh(citation)
                print(f"✅ Citation #{i} insérée avec succès : {citation.id}")
            except Exception as e:
                print(f"⚠️ Erreur à l’insertion de la citation #{i} → {e}")

        db.commit()
        return article

    except SQLAlchemyError as db_err:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur base de données : {str(db_err)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")
