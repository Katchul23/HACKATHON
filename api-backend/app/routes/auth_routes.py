from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, UserUpdate
from app.utils.auth import hash_password, verify_password, create_access_token, decode_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime



router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔐 Route d'enregistrement
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
        # Tous les autres champs ont une valeur par défaut dans le modèle
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ✅ Login compatible OAuth2 (Swagger)
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 💡 form_data.username = email dans notre cas
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Compte non vérifié")

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte inactif")

    return user

@router.put("/admin/update_user/{user_id}", response_model=UserOut)
def admin_update_user(
    user_id: int,
    user_data: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_token(token)
    email = payload.get("sub")

    requesting_user = db.query(User).filter(User.email == email).first()
    if not requesting_user or not requesting_user.is_superuser:
        raise HTTPException(status_code=403, detail="Accès interdit")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if user_data.username is not None:
        user.username = user_data.username

    if user_data.email and user_data.email != user.email:
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        user.email = user_data.email

    if user_data.password is not None:
        user.hashed_password = hash_password(user_data.password)

    if user_data.role is not None:
        user.role = user_data.role

    if user_data.is_active is not None:
        user.is_active = int(user_data.is_active)

    if user_data.is_verified is not None:
        user.is_verified = int(user_data.is_verified)

    db.commit()
    db.refresh(user)
    return user


@router.put("/update", response_model=UserOut)
def update_user(
    user_update: UserUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # 🔁 Mise à jour conditionnelle
    if user_update.username:
        user.username = user_update.username

    if user_update.email and user_update.email != user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        user.email = user_update.email

    if user_update.password:
        user.hashed_password = hash_password(user_update.password)

    if user_update.role and user.is_superuser:
        user.role = user_update.role  # seule les superusers peuvent modifier le rôle

    db.commit()
    db.refresh(user)
    return user

@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    return {"message": "Déconnexion réussie"}

@router.get("/verify/{email}")
def verify_email(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    user.is_verified = True
    db.commit()
    return {"message": "Email vérifié avec succès"}

@router.get("/users", response_model=list[UserOut])
def list_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_superuser:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")

    return db.query(User).all()

@router.delete("/delete/{user_id}")
def delete_user(user_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    email = payload.get("sub")
    admin = db.query(User).filter(User.email == email).first()
    if not admin or not admin.is_superuser:
        raise HTTPException(status_code=403, detail="Accès refusé")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(user)
    db.commit()
    return {"message": "Utilisateur supprimé avec succès"}

@router.get("/check_token")
def check_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token invalide")
        return {"email": email, "valid": True}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token invalide: {str(e)}")
