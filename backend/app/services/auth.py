
import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class AuthError(Exception):
    def __init__(self, detail: str, status_code: int = 401):
        self.detail = detail
        self.status_code = status_code


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(data: dict) -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("Falta configurar JWT_SECRET_KEY")

    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire})

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
