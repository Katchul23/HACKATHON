# scripts/create_superuser.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import SessionLocal
from app.models.user import User
from app.utils.auth import hash_password
# ...


db = SessionLocal()

email = "admin@datatrace.ai"
username = "admin"
password = "Admin123!"

existing = db.query(User).filter(User.email == email).first()
if existing:
    print("❌ Superuser déjà existant.")
else:
    superuser = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_active=1,
        is_verified=1,
        is_superuser=1,
        role="admin"
    )
    db.add(superuser)
    db.commit()
    print("✅ Superuser créé avec succès.")
