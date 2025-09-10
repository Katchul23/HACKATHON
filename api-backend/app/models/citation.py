# app/models/citation.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.config import Base

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    texte = Column(Text, nullable=False)
    type_de_donnee = Column(String, nullable=True)   # "primaire", "secondaire", etc.
    contexte = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    source_metadata = Column(Text, nullable=True)  # Stocké en JSON (as string ici pour simplicité)

    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    # 🔗 Lien vers Article
    article = relationship("Article", back_populates="citations")
    
    def __repr__(self):
        return f"<Citation(id={self.id}, texte={self.texte[:50]}, type_de_donnee={self.type_de_donnee})>"