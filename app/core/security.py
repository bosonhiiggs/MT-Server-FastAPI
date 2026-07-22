from datetime import timedelta, datetime, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode: dict = data.copy()
    # timezone.utc нужен, чтобы время токена было в UTC, иначе могут быть проблемы с валидацией на разных серверах
    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    # "exp" (expiration) — стандартный claim в JWT, используется при decode() для проверки жизненного цикла токена
    to_encode.update({
        "sub": str(data["sub"]),
        "exp": expire,
    })
    encoded_jwt: str = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    result: dict = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    return result
