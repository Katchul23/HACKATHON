from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)   
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    is_superuser = Column(Integer, default=0)  # 1 for superuser, 0 for regular user
    is_verified = Column(Integer, default=0)  # 1 for verified, 0 for unverified
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"