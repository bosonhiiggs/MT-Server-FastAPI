from sqlalchemy import select, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.users.models import UserAccount
from app.users.schemas import UserCreate


async def create_user(user_create: UserCreate, db: AsyncSession) -> UserAccount:
    """
    Функция создания нового пользователя
    :param user_create: объект с параметрами нового пользователя
    :param db: сессия базы данных
    :return: объект созданного аккаунта
    """

    stmt: Select = select(UserAccount).where(UserAccount.username == user_create.username)
    result: Result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Username уже зарегистрирован")

    email_stmt: Select = select(UserAccount).where(UserAccount.email == user_create.email)
    email_result: Result = await db.execute(email_stmt)
    if email_result.scalar_one_or_none():
        raise ValueError("Email уже зарегистрирован")

    new_user: UserAccount = UserAccount(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hash_password(user_create.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def authenticate_user(
        username: str | None,
        email: str | None,
        password: str,
        db: AsyncSession
) -> UserAccount | None:
    """
    Функция авторизации пользователей
    :param username: имя пользователя (опционально)
    :param email: почта пользователя (опционально)
    :param password: пароль пользователя
    :param db: сессия базы данных
    :return: объект авторизированного аккаунта
    """
    if username:
        stmt: Select = select(UserAccount).where(UserAccount.username == username) # type: ignore
    elif email:
        stmt: Select = select(UserAccount).where(UserAccount.email == email) # type: ignore
    else:
        raise ValueError("Должен быть указан username или email")

    result: Result = await db.execute(stmt)
    user: UserAccount | None = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

