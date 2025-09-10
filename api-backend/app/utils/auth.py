from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

# Configuration
SECRET_KEY = "supersecretkey123"  # utilise .env en prod
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
def get_current_user(token: str):
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return user_id  # ou charger l'utilisateur depuis la DB si nécessaire
    except JWTError:
        return None