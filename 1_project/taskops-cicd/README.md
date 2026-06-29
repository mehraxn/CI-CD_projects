# TaskOps

A small Flask task tracker built as a CI/CD portfolio project. Add tasks, mark
them complete, delete them — with an "ops console" UI and a `/health` endpoint
for probes.

## Architecture

Application-factory pattern with a clear separation of concerns:

```
app/
  __init__.py   # create_app() factory: config, logging, blueprint, schema
  config.py     # configuration from env vars (no hardcoded secrets)
  database.py   # SQLite data layer (parameterized queries only)
  routes.py     # thin HTTP handlers
  templates/    # Jinja templates
  static/css/   # ops-console stylesheet
wsgi.py         # gunicorn entry point (wsgi:app)
tests/          # pytest suite
```

## Configuration

| Variable           | Default          | Purpose                  |
| ------------------ | ---------------- | ------------------------ |
| `FLASK_SECRET_KEY` | dev fallback     | Flask session secret     |
| `DATABASE_PATH`    | `taskops.db`     | SQLite database location |
| `MAX_TITLE_LENGTH` | `120`            | Max task title length    |

## Local development

```bash
python -m venv .venv
. .venv/Scripts/activate          # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements-dev.txt

# Run (dev server)
python wsgi.py

# Run (production-style)
gunicorn wsgi:app
```

Confirm it is up:

```bash
curl http://127.0.0.1:5000/health
# {"status":"ok"}
```

## Quality gates

```bash
black --check .
isort --check-only .
ruff check .
bandit -r app
pip-audit
pytest
```
