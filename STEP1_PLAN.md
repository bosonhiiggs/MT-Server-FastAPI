# Step 1: Users/Auth Vertical Slice — План и статусы

Цель: реализовать полный цикл Users/Auth (model → schema → signup/login endpoints → JWT → tests) на одном компактном домене, чтобы упражнить все архитектурные слои один раз перед усложнением.

## Инфраструктура (базовая)

- [x] `pyproject.toml` — зависимости (alembic, asyncpg, fastapi, sqlalchemy, pyjwt, passlib, pytest, uvicorn и т.д.)
- [x] `app/core/config.py` — Settings с env_file=".env", database_url, secret_key, access_token_expire_minutes
- [x] `.env` — переменные окружения заполнены (DATABASE_URL, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)
- [x] `docker-compose.yaml` — Postgres контейнер на порту 5434, volumes объявлены
- [x] Контейнер БД поднят и доступен на localhost:5434

## ORM и БД

- [x] `app/core/db.py` — create_async_engine, Base(DeclarativeBase), async_sessionmaker, get_db() зависимость с yield
- [x] `app/users/models.py` — UserAccount с полями: id, username, email, hashed_password, is_active, is_superuser, created_at
- [ ] Alembic init и конфигурация (env.py для async engine)
- [ ] Первая миграция (users table)
- [ ] Применение миграции (alembic upgrade head)

## API слой (Pydantic схемы)

- [x] `app/users/schemas.py` — UserCreate, UserLogin, UserResponse

## Бизнес-логика

- [x] `app/core/security.py` — hash_password(), verify_password(), create_access_token(), decode_access_token()
- [ ] `app/users/service.py` — UserService.create_user(), authenticate_user()
- [ ] `app/users/dependencies.py` — get_current_user() через OAuth2PasswordBearer + decode JWT

## Роутер и эндпоинты

- [ ] `app/users/router.py` — POST /signup, POST /login, GET /me
- [ ] main.py — подключить router к FastAPI app

## Тестирование

- [ ] Conftest с async fixtures (async engine, test DB)
- [ ] `app/users/tests/test_auth.py` — тесты signup/login/get_me/invalid_token
- [ ] Все тесты проходят (pytest)

## Ручной тест

- [ ] `/docs` Swagger UI доступен
- [ ] Smoke test: signup → login → GET /me → обновление токена

## Notes

- Без `is_activated`/email-верификации в этом шаге (отложено).
- Без аватаров (файловая система — Step финальный).
- Без `is_moderator` (появится с курсами).