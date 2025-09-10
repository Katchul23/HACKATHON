# File: api-backend/app/routes/chat_routes.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.models.article import Article
from app.models.citation import Citation
from app.models.chat import ChatRequest, ChatMessage
from app.services.analyse_service import analyser_article
from app.services.prompt import interpret_prompt, extract_doi
from datetime import datetime
import tempfile, os


router = APIRouter(prefix="/chat", tags=["Chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    prompt = req.prompt.strip()
    session_id = req.sessionId
    context = req.context or {}
    expecting = req.expecting
    print("👉 Prompt reçu :", prompt)

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt vide")

    # 🎯 Si on attendait une info du user (ex: DOI)
    if expecting == "doi":
        doi_candidate = extract_doi(prompt)
        print("👉 DOI détecté :", doi_candidate)

        if not doi_candidate:
            return {
                "response": "Je n’ai pas reconnu de DOI. Peux-tu le reformuler ?",
                "context": { "expecting": "doi", "pending_prompt": prompt }
            }
        prompt = f"{context.get('pending_prompt', '')} {doi_candidate}"
        context = {}
        expecting = None

    parsed = interpret_prompt(prompt)
    print("🎯 Action interprétée :", parsed)

    action = parsed["action"]

    if action == "awaiting_doi":
        return {
            "response": "🔎 Pour continuer, peux-tu me fournir le DOI de l’article ?",
            "context": {
                "expecting": "doi",
                "pending_prompt": parsed.get("pending_prompt"),
                "last_action": "citations"
            }
        }

    if action == "analyse":
        try:
            result = analyser_article(source=parsed["source"], section="all")
            doi = result.get("doi") or (parsed["source"] if parsed["source"].startswith("10.") else None)

            article = Article(
                titre=result.get("titre", "Titre inconnu"),
                doi=doi,
                section_analysee="all",
                texte_source=result.get("texte_source", parsed["source"]),
                auteurs=result.get("auteurs", "Inconnu"),
                date_analyse=result.get("date_analyse", datetime.utcnow())
            )
            db.add(article)
            db.commit()
            db.refresh(article)

            citations = []
            for c in result.get("citations", []):
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
                citations.append(citation)

            db.commit()

            user_msg = ChatMessage(role="user", text=prompt, session=article)
            bot_msg = ChatMessage(role="assistant", text=f"📊 Analyse terminée : {len(citations)} citation(s) détectée(s).", session=article)
            db.add_all([user_msg, bot_msg])
            db.commit()

            return {
                "response": f"📊 Analyse terminée : {len(citations)} citation(s) détectée(s).",
                "context": {
                    "article": article.__dict__,
                    "citations": [c.__dict__ for c in citations]
                }
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur d’analyse : {str(e)}")

    elif action == "citations":
        doi = parsed["doi"]
        type_citation = parsed["type"]
        article = db.query(Article).filter(Article.doi == doi).first()
        if not article:
            return { "response": f"Aucun article trouvé pour le DOI {doi}." }

        citations = db.query(Citation).filter(
            Citation.article_id == article.id,
            Citation.type_de_donnee == type_citation
        ).all()

        user_msg = ChatMessage(role="user", text=prompt, session=article)
        bot_msg = ChatMessage(role="assistant", text=f"🔍 {len(citations)} citation(s) {type_citation} détectée(s).", session=article)
        db.add_all([user_msg, bot_msg])
        db.commit()

        return {
            "response": f"🔍 {len(citations)} citation(s) {type_citation} détectée(s).",
            "context": {
                "article": article.__dict__,
                "citations": [c.__dict__ for c in citations]
            }
        }
    
    elif action == "show_citations":
        doi = parsed.get("source")
        if not doi:
            return {
                "response": "Je n’ai pas le DOI pour retrouver ces citations. Peux-tu me le redonner ?",
                "context": {"expecting": "doi", "pending_prompt": prompt}
            }
        article = db.query(Article).filter(Article.doi == doi).first()
        if not article:
            return {"response": f"Aucun article trouvé pour le DOI {doi}."}

        citations = db.query(Citation).filter(Citation.article_id == article.id).all()
        if not citations:
            return {"response": "Aucune citation enregistrée pour cet article."}

        citation_texts = "\n\n".join([f"- {c.texte[:200]}..." for c in citations])
        return {
            "response": f"Voici les citations extraites :\n\n{citation_texts}",
            "context": { "last_doi": doi, "last_action": "show_citations" }
        }

    elif action == "summary":
        return { "response": "📝 La fonctionnalité de résumé est en cours de développement." }

    return {
        "response": "❓ Je n’ai pas compris votre demande. Essayez avec un DOI ou un extrait d’article.",
        "context": {}
    }


@router.get("/history")
def get_chat_history(db: Session = Depends(get_db)):
    sessions = db.query(Article).order_by(Article.date_analyse.desc()).all()
    return {
        "sessions": [
            {
                "id": s.id,
                "titre": s.titre,
                "doi": s.doi,
                "date_analyse": s.date_analyse.isoformat()
            } for s in sessions
        ]
    }

@router.get("/history/{session_id}")
def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == session_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Session introuvable")

    messages = [
        {
            "sender": m.role,  # 🔁 pour correspondre à `ChatMessage.sender` dans le frontend
            "text": m.text,
            "timestamp": m.timestamp.isoformat()
        }
        for m in article.messages  # via relationship
    ]

    return {
        "session": {
            "id": article.id,
            "titre": article.titre,
            "doi": article.doi,
            "auteurs": article.auteurs,
            "date_analyse": article.date_analyse.isoformat()
        },
        "messages": messages
    }


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont autorisés")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        result = analyser_article(source=tmp_path, section="all")
        os.unlink(tmp_path)

        article = Article(
            titre=result.get("titre", "Titre inconnu"),
            doi=None,
            section_analysee="all",
            texte_source=result.get("texte_source", ""),
            auteurs=result.get("auteurs", "Inconnu"),
            date_analyse=result.get("date_analyse", datetime.utcnow())
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        citations = []
        for c in result.get("citations", []):
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
            citations.append(citation)

        db.commit()

        user_msg = ChatMessage(role="user", text=f"📎 Fichier envoyé : {file.filename}", session=article)
        bot_msg = ChatMessage(role="assistant", text=f"📄 Analyse du fichier réussie. {len(citations)} citation(s) détectée(s).", session=article)
        db.add_all([user_msg, bot_msg])
        db.commit()

        return {
            "response": f"📄 Analyse du fichier réussie. {len(citations)} citation(s) détectée(s).",
            "context": {
                "article": article.__dict__,
                "citations": [c.__dict__ for c in citations],
                "preview": result.get("texte_source", "")[:800] + "..."
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d’analyse du fichier : {str(e)}")
