# Заметки о миграции: Django → FastAPI

## Обзор

Переписка проекта `MT-Server` (Django) на FastAPI + SQLAlchemy 2.0. Целью миграции является исправление архитектурных проблем исходного проекта:
- Отсутствие тестов
- Монолитная структура (god-файл views.py на 1700 строк)
- Рассеянная конфигурация
- Синхронная модель I/O

## Структура исходного проекта

| Приложение | Функциональность | Статус миграции |
|-----------|-----------------|-----------------|
| `accounts/` | Управление пользователями, JWT | [DONE] Step 1: Завершено |
| `catalog/` | Курсы, модули, уроки, рейтинги | [TODO] Step 2: Планируется |
| `musicApi/` | REST API | [TODO] Step 2-3: Рефакторинг |

## Архитектурные решения

### Выбор технологий

| Критерий | Django | FastAPI |
|----------|--------|---------|
| Модель I/O | WSGI (синхронная) | ASGI (асинхронная) |
| Конкурентность | Поток на запрос | Event loop |
| ORM | Django ORM | SQLAlchemy 2.0 |
| Конфигурация | Разбросана по файлам | Centralized (Pydantic Settings) |
| Структура | Слои по типам | Домены |

### Ключевые изменения

**1. Слой моделей**
- `AbstractUser` + `DirtyFieldsMixin` → SQLAlchemy ORM с `Mapped` типами
- Неявное хэширование на `save()` → Явный вызов `hash_password()` в service слое
- Магические методы → Явная логика

**2. Валидация**
- DRF serializers → Pydantic schemas
- Структура: `@api_view` → FastAPI `@app.post()` / `@app.get()`

**3. Конфигурация**
- Scattered `getenv()` вызовы → `pydantic.BaseSettings`
- Без валидации → Типизированная валидация при старте

**4. Аутентификация**
- `djangorestframework-simplejwt` → `pyjwt` + `passlib`
- Упрощённая система разрешений (is_superuser)

**5. Организация кода**
- Слоистая архитектура (views/, models/, serializers/) → Доменная структура
  - users/, courses/, content/
  - Каждый домен: models.py, schemas.py, service.py, router.py, dependencies.py
  - Решает проблему god-файла

## План миграции

### [DONE] Step 1: Users/Auth вертикальный срез (завершено)

Реализовано:
- POST /users/signup — регистрация пользователя
- POST /users/login — вход, возврат JWT токена
- GET /users/me — получить текущего пользователя
- Хэширование пароля (bcrypt)

Исключено из Step 1:
- Верификация email (отложено)
- Загрузка аватара (отложено на Step 3)
- Refresh tokens (отложено на Step 2)
- Сброс пароля (отложено)

### [TODO] Step 2: CRUD домены + Тестирование

Планируется:
- Course, Module, Lesson модели
- CRUD операции (create, list, detail, update, delete)
- pytest + pytest-asyncio тесты
- SQLite in-memory тестовая БД
- Refresh token реализация (опционально)

### [TODO] Step 3: Полиморфный Content + Файлы

- Content полиморфный тип (Text, Video, Image, File, Task)
- SQLAlchemy: single-table или joined-table inheritance
- File upload и storage strategy
- Cascade delete логика

## Сравнение подходов

### Исправленные проблемы

| Проблема | Django | FastAPI |
|----------|--------|---------|
| God-файл | views.py 1700 строк | Роутеры по доменам <100 строк |
| Конфиг | getenv() везде | Pydantic Settings (одно место) |
| Тесты | Отсутствуют | От начала (Step 2) |
| Асинхронность | Синхронная везде | Асинхронная везде |
| Обработка ошибок | try/except в views | HTTPException (автоматическая обработка) |

### Отложенные функции

| Функция | Причина отложения | Когда добавить |
|---------|------------------|-----------------|
| Email верификация | Сложность SMTP логики | Step 2 (если требуется) |
| Refresh tokens | Требует таблицы + логики | Step 2 (с тестами) |
| File uploads | Требует storage strategy | Step 3 |
| Polymorphic Content | Самый сложный migration piece | Step 3 |

## Технические детали

### Хэширование пароля: явность вместо магии

Django подход (неявный):
```python
class CustomAccount(AbstractUser, DirtyFieldsMixin):
    def save(self):
        if 'password' in self.get_dirty_fields():
            self.password = make_password(self.password)
```

FastAPI подход (явный):
```python
hashed_password = hash_password(user_create.password)
new_user = UserAccount(
    username=...,
    hashed_password=hashed_password
)
```

### Конфигурация: типизация и валидация

Django подход:
```python
SECRET_KEY = os.getenv('SECRET_KEY')  # Может быть None
```

FastAPI подход:
```python
class Settings(BaseSettings):
    secret_key: str  # Обязателен
    access_token_expire_minutes: int  # Типизирован
```

При старте приложения все переменные валидируются, None или неправильные типы вызовут ошибку сразу.

## Использованные библиотеки

**ORM и миграции:**
- SQLAlchemy 2.0 (async)
- Alembic

**Валидация:**
- Pydantic
- pydantic-settings

**Аутентификация:**
- pyjwt
- passlib (bcrypt)

**Web-фреймворк:**
- FastAPI
- uvicorn
- python-multipart

**Тестирование:**
- pytest
- pytest-asyncio
- httpx

## Ссылки на ресурсы

- Исходный проект: `/home/yurgen/PycharmProjects/MT-Server`
- FastAPI документация: https://fastapi.tiangelo.com
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic миграции: https://alembic.sqlalchemy.org
- Pydantic: https://docs.pydantic.dev