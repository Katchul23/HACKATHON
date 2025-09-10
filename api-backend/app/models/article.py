# app/models/article.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=True)
    doi = Column(String, unique=True, index=True, nullable=True)
    auteurs = Column(String, nullable=True)
    section_analysee = Column(Text, default="méthodologie")
    texte_source = Column(Text, nullable=True)
    date_analyse = Column(DateTime, default=datetime.utcnow)
    # Dans class Article(Base):
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete")

    # 🔗 Relation avec Citation
    citations = relationship("Citation", back_populates="article", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Article(id={self.id}, titre={self.titre[:50]}, doi={self.doi})>"
