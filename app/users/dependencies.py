import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.db import get_db
from app.core.security import decode_access_token
from app.users.models import UserAccount

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> UserAccount:
    """
    Зависимость для защиты эндпоинтов и получения текущего пользователя из токена
    :param token: JWT токен
    :param db: сессия базы данных
    :return: аккаунт пользователя
    """
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decode_result: dict = decode_access_token(token=token)
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    user_id: int = int(decode_result["sub"])
    stmt: Select = select(UserAccount).where(UserAccount.id == user_id)
    result: Result = await db.execute(stmt)
    user: UserAccount | None = result.scalar_one_or_none()
    if not user:
        raise credentials_exception
    return user
