# AGENTS.md

## Project

Django REST API boilerplate — AI-native, production-ready scaffold for building REST APIs with Django.

Update this section with your project name and one-line description when you clone this repo.

## Tech Stack

- Python 3.13
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- uv
- pytest
- Ruff

## API Versioning

All API routes are versioned under `/api/v1/`.
Register new app URLs in `config/api_v1.py`.
When a breaking change requires v2, add `config/api_v2.py` and register it in `config/urls.py`.
Views receive the active version via `request.version`.

## Architecture

Business logic must live in services.

Views:
- Handle HTTP request/response only.

Serializers:
- Validate API input/output.

Services:
- Business logic and state changes.

Selectors:
- Database read/query logic.

Models:
- Database structure and model-level constraints.

Integrations:
- External APIs, providers, MCP servers, SDK clients.

## Commands

Install:
  uv sync

Run development server:
  uv run python src/manage.py runserver

Tests:
  uv run pytest

Run one test:
  uv run pytest src/apps/users/tests/test_services.py

Lint:
  uv run ruff check .

Format:
  uv run ruff format .

Django checks:
  uv run python src/manage.py check

## Development Rules

1. Read the relevant feature specification before implementation.
2. Inspect existing patterns before creating new architecture.
3. Do not put business logic inside views.
4. Add tests for new behavior.
5. Do not modify unrelated files.
6. Do not introduce dependencies without justification.
7. Never manually edit existing migrations.
8. Never access production credentials.
9. Run tests before considering a task complete.
10. Update documentation when architecture or behavior changes.

## Definition of Done

A task is complete only when:
- Acceptance criteria are satisfied.
- Tests are added.
- Existing tests pass.
- Ruff passes.
- Django system checks pass.
- Documentation is updated where necessary.
