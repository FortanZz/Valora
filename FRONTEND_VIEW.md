# Valora Frontend View

Use this file when you only need to open the website UI.

## Start The Frontend

```bash
cd frontend
npm ci
REACT_APP_API_BASE=http://127.0.0.1:8000/api npm start
```

Open:

```text
http://localhost:3000
```

The frontend has seeded dummy property data with clean real-estate images, so the homepage, browse page, filters, and listing modals work even if the backend is not running.

## Full App Mode

For login, register, creating listings, and SQLite persistence, run the backend in a second terminal before starting the frontend:

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then run:

```bash
cd frontend
REACT_APP_API_BASE=http://127.0.0.1:8000/api npm start
```

## If The Frontend Breaks

Stop the dev server with `Ctrl+C`, then clear the React cache:

```bash
cd frontend
rm -rf node_modules/.cache
npm start
```

If port `3000` is already busy:

```bash
cd frontend
PORT=3001 REACT_APP_API_BASE=http://127.0.0.1:8000/api npm start
```

Open:

```text
http://localhost:3001
```
