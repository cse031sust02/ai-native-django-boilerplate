# AI-Native Django Boilerplate

A production-ready Django REST API scaffold designed for humans and AI coding agents.

> **Core principle:** Make the repository itself the context and operating system for your coding agents.

## What This Is

A starting point for Django REST API projects that are built with AI assistance from day one. The structure, documentation, and workflow conventions are designed so that a coding agent can open the repo, understand the rules, read a feature spec, implement a task, and produce a reviewable pull request — without needing a long custom prompt every time.

## Stack

- Python 3.13
- Django + Django REST Framework
- PostgreSQL
- Redis + Celery
- uv (package manager)
- pytest + Ruff

## Quick Start

**With Docker (recommended):**

```bash
git clone <this-repo> myproject
cd myproject
cp .env.example .env          # edit DB name and SECRET_KEY
docker compose up
```

Django runs at `http://localhost:8000`. Migrations apply automatically on startup.

**Without Docker:**

```bash
uv sync
cp .env.example .env          # set DATABASE_URL and SECRET_KEY
uv run python src/manage.py migrate
uv run python src/manage.py runserver
```

Verify: `curl http://localhost:8000/health/` should return `{"status": "ok"}`.

## Starting a New Project from This Boilerplate

1. Clone or use this repo as a GitHub template.
2. Find and replace `myproject` with your project name in:
   - `pyproject.toml` (project name and description)
   - `.env.example` (database name)
   - `docker-compose.yml` (service names if desired)
3. Update `README.md`, `AGENTS.md`, and `ARCHITECTURE.md` with your project context.
4. Generate a new `SECRET_KEY`:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
5. Run `docker compose up` and verify `/health/` returns 200.
6. Create `src/config/settings/production.py` before any deployment.

## How to Develop a Feature (AI-Native Workflow)

```
1. Write a spec          →  specs/active/my-feature.md
2. Break into tasks      →  tasks/TASK-001-my-feature.md
3. Agent implements      →  reads AGENTS.md + spec, implements, adds tests
4. Verify                →  pytest + ruff + django check
5. Review & merge        →  PR
6. Archive the spec      →  specs/active/ → specs/completed/
```

Use the templates:
- `specs/template.md` — feature specification template
- `tasks/template.md` — agent task template

## Adding a New App

```bash
# 1. Create the app directory
mkdir -p src/apps/myapp/tests
touch src/apps/myapp/{__init__.py,apps.py,models.py,selectors.py,services.py,serializers.py,views.py,urls.py,admin.py}
touch src/apps/myapp/migrations/__init__.py
touch src/apps/myapp/tests/{__init__.py,test_models.py,test_services.py,test_views.py}

# 2. Register in INSTALLED_APPS
# src/config/settings/base.py → add "apps.myapp"

# 3. Register URL routes
# src/config/api_v1.py → add path("myapp/", include("apps.myapp.urls"))
```

Each layer has a single responsibility — see `ARCHITECTURE.md` for the full contract.

## Project Structure

```
├── src/
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py         # Shared settings, env-driven
│   │   │   ├── local.py        # Dev overrides
│   │   │   └── production.py   # Create this before deploying
│   │   ├── urls.py
│   │   ├── api_v1.py           # All /api/v1/ routes
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── apps/
│       ├── health/             # Health check endpoint (keep this)
│       └── <your-domain>/      # Add your domain apps here
├── docs/
│   ├── architecture/           # Architecture notes per concern
│   ├── decisions/              # ADRs (why we chose X)
│   ├── features/               # Feature-level documentation
│   └── deployment/             # Local, staging, production guides
├── specs/
│   ├── active/                 # In-progress feature specs
│   ├── completed/              # Done specs (archived here)
│   └── template.md
├── tasks/
│   └── template.md             # Agent-friendly task template
├── tests/                      # Project-wide integration / e2e tests
├── AGENTS.md                   # Agent operating manual (read first)
├── ARCHITECTURE.md             # System design overview
└── docker-compose.yml
```

## Key Commands

```bash
uv run python src/manage.py runserver   # Dev server
uv run pytest                           # All tests
uv run ruff check .                     # Lint
uv run ruff format .                    # Format
uv run python src/manage.py check       # Django system checks
uv run python src/manage.py makemigrations <app>
uv run python src/manage.py migrate
```

## API Versioning

All routes live under `/api/v1/`. Register new apps in `src/config/api_v1.py`.

When a breaking change requires v2: create `src/config/api_v2.py` and add `path("api/v2/", include(("config.api_v2", "v2")))` to `config/urls.py`. Views can branch on `request.version`.

## Environment Variables

| Variable              | Required | Default                    | Notes                      |
|-----------------------|----------|----------------------------|----------------------------|
| `SECRET_KEY`          | Yes      | —                          | Fails at startup if missing |
| `DATABASE_URL`        | No       | SQLite                     | Parsed by dj-database-url  |
| `REDIS_URL`           | No       | `redis://localhost:6379/0` | Celery broker              |
| `ALLOWED_HOSTS`       | No       | `localhost,127.0.0.1`      | Comma-separated            |
| `CORS_ALLOWED_ORIGINS`| No       | `""` (empty)               | Comma-separated            |
| `DEBUG`               | No       | `False`                    | Set `True` for local dev   |

## Contributing

1. Read `AGENTS.md` and `ARCHITECTURE.md`.
2. Write a spec in `specs/active/` before implementing.
3. Keep business logic in services, not views.
4. Add tests for new behavior.
5. Ensure `pytest`, `ruff check .`, and `manage.py check` all pass.

## License

MIT
