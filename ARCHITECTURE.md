# ARCHITECTURE.md

## Overview

This is an AI-native Django REST API boilerplate. It provides a layered architecture where business logic, HTTP handling, validation, and data access each have a clearly bounded responsibility. This separation makes the codebase predictable for both humans and coding agents.

Update this document with your project's domain context when you use this boilerplate.

## Request Flow

```
HTTP Request
    |
    v
  View               (HTTP request/response only)
    |
    v
Serializer           (input validation and output representation)
    |
    v
Service  <---------- (business logic and state changes)
  /    \
 v      v
Selector  Integration  (DB queries)  (external APIs, AI, MCP)
  |
  v
Model                (database structure)
```

## Layer Responsibilities

| Layer        | Responsibility                                      |
|-------------|------------------------------------------------------|
| Views        | HTTP request/response handling only                 |
| Serializers  | Input validation and API representation             |
| Services     | Business logic and state changes                    |
| Selectors    | Database read/query logic                           |
| Models       | Database structure and model-level constraints      |
| Integrations | External vendors, APIs, MCP servers, SDK clients    |

## Separation of Concerns

```
apps/          → Business/domain logic (one app per bounded context)
integrations/  → External vendors, APIs, MCP, SDKs
```

## Key Design Decisions

See [docs/decisions/](docs/decisions/) for Architecture Decision Records (ADRs).

## Domain Apps

Apps live under `src/apps/`. Each follows the standard structure:

```
apps/<domain>/
  __init__.py
  apps.py
  models.py
  migrations/
  selectors.py
  services.py
  serializers.py
  views.py
  urls.py
  admin.py
  tests/
    test_models.py
    test_selectors.py
    test_services.py
    test_views.py
```

### Registering a new app

1. Add `"apps.<domain>"` to `INSTALLED_APPS` in `config/settings/base.py`.
2. Add `path("<domain>/", include("apps.<domain>.urls"))` in `config/api_v1.py`.

## API Versioning

All routes are namespaced under `/api/v1/`. DRF `NamespaceVersioning` propagates the version to `request.version` in every view. A future breaking change gets `config/api_v2.py`; v1 stays live until clients migrate.

There is an unversioned `/health/` endpoint for infrastructure probes.

## Background Jobs

Celery with Redis as broker. Task modules live at `apps/<domain>/tasks.py`. See [docs/architecture/background-jobs.md](docs/architecture/background-jobs.md) for patterns.

## Further Reading

- [Architecture Overview](docs/architecture/overview.md)
- [Authentication](docs/architecture/authentication.md)
- [Background Jobs](docs/architecture/background-jobs.md)
- [Database](docs/architecture/database.md)
- [ADRs](docs/decisions/)
