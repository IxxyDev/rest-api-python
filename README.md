# Как запустить

## Локально (SQLite)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]

export API_KEY=local-dev-key
export DATABASE_URL=sqlite+aiosqlite:///./app.db

alembic upgrade head
python -m app.seeds  # опционально
uvicorn app.main:app --reload
```

## Docker
```bash
docker build -t org-directory .
docker run \
  -e API_KEY=<your-key> \
  -e DATABASE_URL=sqlite+aiosqlite:///./app.db \
  -p 8000:8000 \
  org-directory
```

## Docker Compose (PostgreSQL)
```bash
API_KEY=<your-key> docker compose up --build
```
