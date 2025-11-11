# Running & Deployment Instructions

## Local Development
1. Install Python 3.14 (project metadata stays compatible with 3.9+ if needed).
2. Create a virtual environment: `python3.14 -m venv .venv && source .venv/bin/activate`.
3. Upgrade pip and install dependencies: `pip install -U pip && pip install -e .[dev]`.
4. Apply database migrations: `alembic upgrade head`.
5. Start the API server: `uvicorn app.main:app --reload`.
6. Run tests whenever you change code: `pytest -q`.

## Production Deployment
1. Build an environment with Python 3.14, FastAPI, SQLAlchemy, Alembic, and uvicorn installed via `pip install .`.
2. Apply Alembic migrations to your target database: `alembic upgrade head`.
3. Configure environment variables (`API_KEY`, `DATABASE_URL`, etc.) before launching.
4. Run the app with a production server, e.g. `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
5. Put the service behind a process manager/reverse proxy (systemd, Supervisor, nginx) for resilience.
