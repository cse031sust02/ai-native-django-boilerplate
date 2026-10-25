# AI-Native Django Boilerplate

## Status
Completed

## Goal
Establish a production-ready, AI-agent-friendly Django REST API scaffold that can be consistently replicated across projects.

## What This Covers

This spec documents the design decisions behind this boilerplate. Every decision here is intentional and reproducible. Use this as the reference when starting a new AI-native Django project.

---

## Directory Structure

```
project-root/
├── src/                          # All Python source code lives here
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py           # Shared settings; env-driven
│   │   │   ├── local.py          # Dev overrides (DEBUG=True, ALLOWED_HOSTS=*)
│   │   │   └── production.py     # Prod overrides (create per project)
│   │   ├── urls.py               # Root URL conf
│   │   ├── api_v1.py             # All /api/v1/ routes aggregated here
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── apps/
│       └── <domain>/             # One directory per bounded domain
│           ├── models.py
│           ├── selectors.py      # DB reads only
│           ├── services.py       # Business logic and state changes
│           ├── serializers.py
│           ├── views.py          # HTTP in/out only
│           ├── urls.py
│           └── tests/
├── docs/
│   ├── architecture/             # Architecture notes (auth, background jobs, db)
│   ├── decisions/                # ADRs (001-use-postgresql.md, etc.)
│   ├── features/                 # Feature-level documentation
│   └── deployment/               # Environment-specific deployment guides
├── specs/
│   ├── active/                   # In-progress feature specs
│   ├── completed/                # Done feature specs (this file lives here)
│   └── template.md               # Blank spec template
├── tasks/
│   └── template.md               # Blank task template for agent work
├── tests/                        # Root-level test directory (project-wide)
├── docker/
│   └── entrypoint.sh
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── .env                          # Gitignored; copy from .env.example
├── .env.example                  # Committed; documents required env vars
├── AGENTS.md                     # Agent operating manual (read by AI agents)
├── ARCHITECTURE.md               # Human-readable architecture overview
└── README.md
```

### Why `src/` layout

All Django source lives under `src/` to:
- Separate source code from project configuration files (Dockerfile, pyproject.toml, docs)
- Prevent accidental imports of project-root files as Python modules
- Align with the `uv` / modern Python packaging convention

This requires `PYTHONPATH=/app/src` in Docker and `pythonpath = ["src"]` in `pyproject.toml` for pytest.

---

## Docker Setup

### Services

| Service | Image | Purpose |
|---------|-------|---------|
| web | project Dockerfile | Django dev/prod server |
| db | postgres:16-alpine | Primary datastore |
| redis | redis:7-alpine | Celery broker + result backend |

All services have healthchecks. `web` depends on `db` and `redis` being healthy before starting.

### Key Dockerfile patterns

```dockerfile
# Copy uv binary from the official image — no separate install step
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# venv lives OUTSIDE /app so the volume mount doesn't shadow it
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app/src

# Layer cache: deps install only when pyproject.toml or uv.lock changes
COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project --no-dev --frozen

COPY . .
```

The `--frozen` flag makes the build deterministic — it refuses to resolve if `uv.lock` is out of date.

### Entrypoint

`docker/entrypoint.sh` runs `migrate --no-input` then `exec "$@"` (passes CMD through). Acceptable for dev and single-container staging; in multi-container production, run migrations as a one-off job, not on every container start.

---

## Settings Architecture

| File | Purpose | DJANGO_SETTINGS_MODULE |
|------|---------|----------------------|
| `base.py` | All shared config, env-driven | — |
| `local.py` | `DEBUG=True`, `ALLOWED_HOSTS=["*"]` | default in manage.py / wsgi / asgi |
| `production.py` | Security headers, `DEBUG=False`, strict hosts | set via env var in deployment |

### Environment variables (base.py)

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `SECRET_KEY` | Yes | — | Hard fails at startup if missing |
| `DATABASE_URL` | No | sqlite | Parsed by `dj-database-url` |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Used by Celery |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated |
| `CORS_ALLOWED_ORIGINS` | No | `""` (empty list) | Comma-separated |
| `DEBUG` | No | `False` | Set `True` in `.env` for local |

---

## API Versioning

DRF `NamespaceVersioning` is used. Every endpoint lives under `/api/v1/`.

```
URL pattern:   /api/v1/<app>/
Namespace:     "v1"
Registered in: src/config/api_v1.py
```

Adding a new app:

```python
# src/config/api_v1.py
urlpatterns = [
    path("health/", include("apps.health.urls")),
    path("users/",  include("apps.users.urls")),   # add here
]
```

For a breaking API change: create `src/config/api_v2.py` and register `path("api/v2/", include(("config.api_v2", "v2")))` in `urls.py`. Views can branch on `request.version`.

### Health check

Two routes are registered:
- `/health/` — for load balancers, Docker healthchecks, k8s probes (no version required)
- `/api/v1/health/` — for API clients that prefer the versioned namespace

Both return:
```json
{
  "status": "ok" | "degraded",
  "checks": { "database": "ok", "redis": "ok" }
}
```
HTTP 200 when healthy, HTTP 503 when degraded. `AllowAny` — no auth required.

---

## App Template

Every new domain follows the same internal structure. Register it in `INSTALLED_APPS` and `config/api_v1.py`.

```
apps/<domain>/
├── __init__.py
├── apps.py
├── models.py
├── migrations/
│   └── __init__.py
├── selectors.py       # Pure reads: get_user_by_id(), list_active_users()
├── services.py        # Writes/logic: create_user(), update_profile()
├── serializers.py     # Input + output shapes
├── views.py           # APIView or ViewSet; delegates to services/selectors
├── urls.py
├── admin.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_selectors.py
    ├── test_services.py
    └── test_views.py
```

### Layer rules

- **Views** call selectors (for reads) and services (for writes). No ORM queries in views.
- **Services** call selectors, models, integrations. Return model instances or dicts. Raise `ValidationError` or custom exceptions for business rule violations.
- **Selectors** only read. Return querysets or model instances. No writes.
- **Integrations** (`src/integrations/<vendor>/`) wrap external APIs — one module per vendor.

---

## Reuse Checklist

When starting a new project from this boilerplate:

- [ ] Clone or use as GitHub template
- [ ] Replace `myproject` with your project name in `pyproject.toml` and `.env.example`
- [ ] Update `README.md`, `AGENTS.md`, and `ARCHITECTURE.md` with project context
- [ ] Generate a new `SECRET_KEY` and set it in `.env`
- [ ] Update `DATABASE_URL` in `.env` with the new DB name
- [ ] Run `docker compose up` — should start cleanly
- [ ] Verify `/health/` returns `200 {"status": "ok"}`
- [ ] Create `config/settings/production.py` before any deployment
- [ ] Add `CORS_ALLOWED_ORIGINS` in `.env` for the frontend domain

---

## Key Dependencies

| Package | Version | Role |
|---------|---------|------|
| Django | ≥5.1 | Web framework |
| djangorestframework | ≥3.15 | REST API layer |
| django-cors-headers | ≥4.0 | CORS for browser clients |
| dj-database-url | ≥2.3 | Parse `DATABASE_URL` env var |
| psycopg[binary] | ≥3.2 | PostgreSQL adapter |
| celery | ≥5.4 | Background task queue |
| redis | ≥5.2 | Celery broker + cache |
| gunicorn | ≥23.0 | Production WSGI server |
| uv | latest | Fast dependency management |
| pytest-django | ≥4.9 | Django test runner integration |
| ruff | ≥0.8 | Linter and formatter |
