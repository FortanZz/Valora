# Valora Backend

FastAPI backend for the Valora real estate platform.

## Requirements

- Python 3.11+
- pip

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your local values before running the app.

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async SQLAlchemy database URL | `sqlite+aiosqlite:///./valora_async.db` |
| `DEBUG` | Enable SQLAlchemy query logging | `false` |
| `JWT_SECRET_KEY` | Secret used to sign JWT tokens | *(required in production)* |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed CORS origins | `http://localhost:3000,http://127.0.0.1:3000` |

Legacy auth endpoints also use a SQLite database file (`valora.db`) created automatically on startup.

## Database migrations (Alembic)

Apply migrations before first run if you use the async SQLAlchemy database:

```bash
cd backend
source .venv/bin/activate
python -m alembic upgrade head
```

Create a new migration after model changes:

```bash
python -m alembic revision --autogenerate -m "describe change"
python -m alembic upgrade head
```

## Run the app

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API runs at `http://127.0.0.1:8000`.

Useful URLs:

- Health check: `GET /api/health`
- Interactive docs: `http://127.0.0.1:8000/docs`

## Run tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

Run a subset:

```bash
python -m pytest -q tests/test_health.py tests/test_properties.py
```

Tests use an in-memory SQLite database and an async `httpx` client.

## API overview

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `GET /api/auth/me`

### Properties

- `GET /api/properties/` — paginated list (`items`, `total`); supports `skip`, `limit`, and `search` (case-insensitive location filter)
- `POST /api/properties/` — create (auth required)
- `GET /api/properties/{id}` — get one
- `PUT /api/properties/{id}` — update (auth required)
- `DELETE /api/properties/{id}` — delete (auth required)
