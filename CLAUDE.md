# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MT-Server-FastAPI** is a portfolio project: a rewrite of an older Django project (`/home/yurgen/PycharmProjects/MT-Server`) into FastAPI + SQLAlchemy 2.0. The source project is a music education platform with courses, modules, lessons, and polymorphic content (text/video/image/files/tasks).

**Key constraint:** This is a learning/portfolio project. Claude should explain concepts and point out issues, but the user writes all code themselves. See `feedback_teaching_mode` in memory for details.

## Architecture

### Structure: Domain-based (not layered-by-type)

Each domain lives in its own folder (`users/`, `courses/`, `content/`, etc.) with its own:
- `models.py` — SQLAlchemy ORM models (inherit from `Base` in `core/db.py`)
- `schemas.py` — Pydantic validation schemas (input/output)
- `service.py` — business logic (queries, transformations, external calls)
- `router.py` — API endpoints (depend on service layer)
- `dependencies.py` — FastAPI `Depends()` functions (e.g., `get_current_user`)
- `tests/` — pytest tests for this domain

Shared infrastructure in `core/`:
- `config.py` — Pydantic Settings (reads `.env`)
- `db.py` — SQLAlchemy async engine, `Base(DeclarativeBase)`, `async_sessionmaker`, `get_db()` dependency
- `security.py` — password hashing, JWT encode/decode (no Django here, all explicit)

### Async-first design

All endpoints, services, and database operations use `async`/`await`. SQLAlchemy engine is created with `create_async_engine()` and uses `asyncpg` driver (not blocking `psycopg2`). Sessions are `AsyncSession` from `async_sessionmaker()`.

### Dependencies via `Depends()`

FastAPI's dependency injection pattern. Example: `get_db()` yields a session and closes it after the endpoint completes (cleanup via code after `yield`).

## Tech Stack

- **Framework:** FastAPI 0.139+
- **ORM:** SQLAlchemy 2.0 (async)
- **Migrations:** Alembic
- **Config:** pydantic-settings (BaseSettings from `.env`)
- **Auth:** JWT (pyjwt) + bcrypt (passlib)
- **Package manager:** `uv` (not Poetry)
- **DB:** PostgreSQL 16 (local via Docker Compose on port 5434)
- **Testing:** pytest + pytest-asyncio + httpx.AsyncClient
- **Dev server:** uvicorn

## Common Commands

```bash
# Dependencies
uv add <package>           # Add dependency
uv remove <package>        # Remove dependency
uv sync                    # Sync pyproject.toml → installed packages
uv run <script>           # Run a script/command in venv context

# Database (local)
docker compose up -d db   # Start Postgres container (port 5434)
docker compose down db    # Stop Postgres

# Migrations (Alembic)
alembic init alembic                    # Initialize Alembic (one-time, repo already has this)
alembic revision --autogenerate -m "description"  # Auto-generate migration from models
alembic upgrade head                    # Apply all pending migrations
alembic downgrade -1                    # Rollback last migration

# Dev server
uvicorn app.main:app --reload          # Start FastAPI dev server (auto-reload on code changes)
# Or from uv context: uv run uvicorn app.main:app --reload

# Tests
pytest                                  # Run all tests
pytest app/users/tests/test_auth.py::test_signup -v  # Single test with verbosity
pytest --tb=short                       # Shorter traceback on failures
```

## Development Workflow

1. **Make code changes** in `app/` (new model, schema, endpoint, etc.)
2. **If ORM models changed:** Generate migration, review it, apply it
   ```bash
   alembic revision --autogenerate -m "add user fields"
   alembic upgrade head
   ```
3. **Test locally:** Start dev server, check `/docs` (Swagger UI), run pytest
4. **Iterate:** Fix issues, re-test

## Configuration

`.env` file (not in git, use `.env.template` as reference):
```
DATABASE_URL=postgresql+asyncpg://mt-user-fastapi:mt-pass-fastapi@localhost:5434/mt-fastapi
SECRET_KEY=<generated-hex-string>
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

`DATABASE_URL` format: `postgresql+asyncpg://user:password@host:port/dbname`. The `asyncpg` driver is required for async support.

## Migration Order (Step-by-step)

See `STEP1_PLAN.md` for current status. Rough plan:
- **Step 0:** Architecture decisions (done)
- **Step 1:** Users/Auth vertical slice (in progress)
  - ORM models, Pydantic schemas, signup/login endpoints, JWT, tests
- **Step 2:** Simple CRUD domains (Course, Module, Lesson)
- **Step 3:** Polymorphic Content + file uploads (hardest part)

## Key Differences from Django Source Project

| Django | FastAPI |
|--------|---------|
| WSGI (sync) | ASGI (async) |
| Django ORM + Django migrations | SQLAlchemy 2.0 + Alembic |
| Poetry | `uv` |
| Scattered `getenv()` config | Pydantic Settings + `.env` |
| `djangorestframework-simplejwt` | `pyjwt` (simpler, more explicit) |
| DirtyFieldsMixin (implicit) | Explicit service layer logic |
| God-file `views.py` (1700 lines) | Domain-based structure (models/schemas/service/router split) |
| No tests | Tests from the start (pytest) |

## Known Limitations (by design for Step 1)

- No email verification (`is_activated` field deferred)
- No avatar uploads (file handling deferred to Step 3)
- No `is_moderator` role (added when courses domain starts)
- `PasswordResetRequest` not implemented yet

## Important Notes

- **Async all the way:** Avoid blocking operations (sync DB calls, time.sleep, blocking I/O). If you must, use `asyncio.to_thread()` or a thread pool.
- **Session cleanup:** Always use `get_db()` dependency in endpoints; don't manually create sessions without proper cleanup.
- **Pydantic != ORM:** Schemas (Pydantic) are separate from models (SQLAlchemy). Schemas validate input, models map to DB tables. Don't mix them.
- **Never expose hashed passwords:** `UserResponse` schema must never include `hashed_password` field.
- **Test DB:** Use in-memory SQLite (`sqlite+aiosqlite:///:memory:`) for tests to avoid polluting the local Postgres.

## References

- FastAPI docs: https://fastapi.tiangolo.com
- SQLAlchemy 2.0 async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic: https://alembic.sqlalchemy.org
- Pydantic docs: https://docs.pydantic.dev