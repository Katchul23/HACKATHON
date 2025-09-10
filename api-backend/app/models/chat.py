# File: app/models/chat.py
# ✅ Schéma Pydantic pour la requête chat
from pydantic import BaseModel
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base  # ou app.database.Base selon ton projet

# ✅ Modèle SQLAlchemy
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)  # 'user' ou 'assistant'
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    session_id = Column(Integer, ForeignKey("articles.id"))
    session = relationship("Article", back_populates="messages")
    

class ChatRequest(BaseModel):
    prompt: str
    sessionId: Optional[int]
    context: Optional[Dict[str, Any]] = None
    expecting: Optional[str] = None
