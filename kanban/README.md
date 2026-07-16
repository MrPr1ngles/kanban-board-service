# Kanban-доска

Аналог Trello: доски, колонки, карточки с drag-and-drop, участники с ролями, комментарии, аудит изменений.

Стек: FastAPI + PostgreSQL + SQLAlchemy/Alembic + React (Vite, @dnd-kit) + Docker Compose.

## Запуск одной командой

```bash
docker compose up --build
```

- Приложение: http://localhost:3000
- Swagger (документация API): http://localhost:8000/docs
- Демо-пользователи: `alice` (owner), `bob` (writer), `carol` (reader), пароль у всех — `password123`

При старте backend сам применяет Alembic-миграции и наполняет базу демо-данными (seed идемпотентен).

## Запуск для разработки (без Docker)

```bash
# Backend (можно на SQLite, Postgres не обязателен)
cd backend
pip install -r requirements.txt
export DATABASE_URL='sqlite:///./dev.db' JWT_SECRET='dev'
python -m alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload --port 8000

# Frontend (в другом терминале; /api проксируется на :8000)
cd frontend
npm install
npm run dev
```

## Архитектура

```
Client (React SPA) → nginx → FastAPI (REST, JWT) → PostgreSQL
```

- **Авторизация**: `POST /api/auth/login` обменивает login+password на JWT; все остальные ручки требуют `Authorization: Bearer <token>`. Пароли хранятся как bcrypt-хэши.
- **RBAC**: роли reader / writer / owner на уровне доски (таблица `board_members`). Чужая доска возвращает 404 — принцип минимальных привилегий.
- **Защита от коллизий**: оптимистичная блокировка через поле `version` у досок и карточек. Конфликт → 409 Conflict, клиент перечитывает состояние.
- **Порядок карточек**: fractional indexing (`position NUMERIC`); вставка между соседями — среднее их позиций, перемещение — UPDATE одной строки.
- **Аудит**: все изменения пишутся в `audit_log` (кто, что, когда, diff в JSONB) в одной транзакции с основной операцией. `GET /api/boards/{id}/audit` — только owner.

## Структура

```
backend/
  app/models/     SQLAlchemy-модели (users, boards, board_members, columns, cards, comments, audit_log)
  app/schemas/    Pydantic-схемы запросов/ответов
  app/core/       security.py (bcrypt, JWT), permissions.py (RBAC)
  app/services/   card_service.py (move в транзакции, проверка версий), audit_service.py
  app/api/        роутеры: auth, boards, members, columns, cards, comments, audit
  migrations/     Alembic
  scripts/seed.py демо-данные
frontend/
  src/pages/      Login, BoardList, Board (DnD)
  src/components/ Column, Card, CardModal, MembersDialog
```

## Наполнение базы

Автоматически при старте контейнера, либо вручную: `python -m scripts.seed`.
