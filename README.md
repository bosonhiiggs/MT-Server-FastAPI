# MT-Server-FastAPI

Переписывание старого Django-проекта (MT-Server) в FastAPI + SQLAlchemy 2.0. Портфолио-проект для демонстрации умения переводить код между фреймворками и архитектурных решений.

## Стек технологий

- **Framework:** FastAPI 0.139+
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Database:** PostgreSQL 16
- **Auth:** JWT (pyjwt) + bcrypt (passlib)
- **Package Manager:** `uv`
- **Testing:** pytest + pytest-asyncio

## Установка и запуск

### Требования
- Python 3.12+
- PostgreSQL 16
- Docker + Docker Compose (опционально, для локальной БД)

### Шаги

1. **Клонируйте репозиторий**
   ```bash
   git clone <repo-url>
   cd MT-Server-FastAPI
   ```

2. **Установите зависимости через `uv`**
   ```bash
   uv sync
   ```

3. **Создайте `.env` файл** из `.env.template`
   ```bash
   cp .env.template .env
   # Отредактируйте .env: заполните SECRET_KEY (openssl rand -hex 32)
   ```

4. **Поднимите локальную Postgres** (если используете Docker Compose)
   ```bash
   docker compose up -d db
   ```

5. **Примените миграции**
   ```bash
   alembic upgrade head
   ```

6. **Запустите dev сервер**
   ```bash
   uv run uvicorn app.main:app --reload
   ```
   
   Swagger UI доступен на `http://localhost:8000/docs`

## Развитие проекта

### Текущий статус: Step 1 (Users/Auth vertical slice)

Реализована инфраструктура и базовый ORM слой для пользователей. В процессе:
- [ ] Сервис-слой (create_user, authenticate_user)
- [ ] Зависимости (get_current_user)
- [ ] Роутер (signup, login, me endpoints)
- [ ] Тесты

### Архитектура

Domain-based структура (не layered-by-type):
```
app/
  core/              # общие: config, db, security
  users/             # домен users: models, schemas, service, router, dependencies, tests
  courses/           # (будущее) домен courses
  content/           # (будущее) домен content (самая сложная часть)
```

## Ссылки

- [FastAPI документация](https://fastapi.tiangelo.com)
- [SQLAlchemy 2.0 async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic](https://alembic.sqlalchemy.org)
- [Исходный Django проект](../MT-Server)