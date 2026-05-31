# Valora

Valora is a React frontend with a FastAPI backend and SQLite persistence.

## Requirements

- Python 3.9+
- Node.js 18+
- npm

## First-Time Setup

Run these from the project root.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

```bash
cd ../frontend
npm ci
```

## Run The App Locally

Open two terminals.

Terminal 1, backend API:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, frontend web app:

```bash
cd frontend
REACT_APP_API_BASE=http://127.0.0.1:8000/api npm start
```

Open the web app at:

```text
http://localhost:3000
```

The backend API runs at:

```text
http://127.0.0.1:8000
```

## Run Tests

Backend tests:

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
```

Frontend production build check:

```bash
cd frontend
npm run build
```

## Serve The Built Web Page

If you want to run the optimized production build locally:

```bash
cd frontend
npm run build
npx serve -s build -l 3000
```

Open:

```text
http://localhost:3000
```

## Useful Notes

- Start the backend before using login, register, search, or listing creation in the frontend.
- The frontend defaults to `http://localhost:8000/api`, but the command above sets `REACT_APP_API_BASE` explicitly to `http://127.0.0.1:8000/api`.
- Local SQLite data is stored in `backend/valora.db`.
- To reset local data, stop the backend and run:

```bash
rm backend/valora.db
```

- If port `3000` or `8000` is already in use, stop the other process or choose another port. If the backend port changes, update `REACT_APP_API_BASE` when starting the frontend.
