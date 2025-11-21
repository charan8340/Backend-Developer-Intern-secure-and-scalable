from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt, hashlib, os
from app.core.config import settings
from typing import Dict

pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(datetime.utcnow().timestamp())})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        print("DEBUG decode_access_token -> payload:", payload)
        return payload
    except jwt.ExpiredSignatureError:
        print("DEBUG decode_access_token -> expired token")
        raise
    except Exception as e:
        print("DEBUG decode_access_token -> exception:", repr(e))
        raise

def generate_refresh_token_raw() -> str:
    return os.urandom(32).hex()

def hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
