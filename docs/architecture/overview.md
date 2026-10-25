# Architecture Overview

This is a Django REST API backend following a layered, service-oriented architecture. All code in this repository follows the conventions described here.

## Source Layout

All Python source lives under `src/` to keep it separate from project-level config (Dockerfile, pyproject.toml, docs). `PYTHONPATH` is set to `/app/src` in Docker so imports resolve without a package prefix.

```
src/
├── config/          # Django project config (settings, urls, wsgi, asgi)
└── apps/            # Domain apps (one directory per bounded context)
```

## Request Pipeline

```
HTTP Request
    │
    ▼
  View               ← HTTP in/out only; no business logic
    │
    ▼
Serializer           ← Validate input; shape output
    │
    ▼
Service              ← Business logic; state changes; raises on rule violations
   / \
  ▼   ▼
Selector  Integration
  │         └─── External APIs, AI providers, MCP servers, SDK clients
  ▼
Model                ← Database structure and constraints
```

## Layer Contracts

**Views** (`views.py`)
- Parse the HTTP request; call a service or selector; return a Response.
- No ORM queries, no business logic.

**Serializers** (`serializers.py`)
- Define the shape of incoming and outgoing data.
- Raise `ValidationError` for malformed input.

**Services** (`services.py`)
- Own all state-changing logic: create, update, delete, trigger side effects.
- May call selectors, models, and integrations.
- Return model instances or plain dicts.
- Named as verbs: `create_user`, `update_profile`, `send_notification`.

**Selectors** (`selectors.py`)
- Read-only. No writes.
- Return querysets or instances.
- Named as queries: `get_user_by_id`, `list_active_users`.

**Integrations** (`src/integrations/<vendor>/`)
- One module per external vendor or provider.
- Wrap SDK calls; translate errors into project-level exceptions.
- Never called from views directly — always via a service.

## App Structure

Each domain app follows this layout:

```
apps/<domain>/
├── __init__.py
├── apps.py
├── models.py
├── migrations/
├── selectors.py
├── services.py
├── serializers.py
├── views.py
├── urls.py
├── admin.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_selectors.py
    ├── test_services.py
    └── test_views.py
```

Register new apps in:
1. `config/settings/base.py` → `INSTALLED_APPS`
2. `config/api_v1.py` → URL routing

## API Versioning

All routes are namespaced under `/api/v1/`. DRF `NamespaceVersioning` propagates the version to `request.version` in every view. A future breaking change gets `config/api_v2.py`; v1 stays live until clients migrate.

There is also an unversioned `/health/` endpoint for infrastructure probes.

## Background Jobs

Celery with Redis as broker. Task modules live at `apps/<domain>/tasks.py`. See [background-jobs.md](background-jobs.md) for patterns.

## Further Reading

- [Authentication](authentication.md)
- [Background Jobs](background-jobs.md)
- [Database](database.md)
- [ADRs](../../docs/decisions/)
