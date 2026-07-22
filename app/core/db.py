from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Движок
engine: AsyncEngine = create_async_engine(settings.database_url)

# Базовый класс для всех будущих ORM-моделей
class Base(DeclarativeBase):
    pass

# expire_on_commit=False нужен для async: иначе после commit() объект инвалидируется,
# и при попытке прочитать его атрибуты в async-контексте без нового запроса будет MissingGreenlet
session: async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db: AsyncSession = session()
    try:
        yield db
    finally:
        await db.close()
