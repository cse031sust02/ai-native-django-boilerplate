# AI-Native Django Boilerplate

> **Make the repository itself the context and operating system for your coding agents.**

A production-ready Django REST API scaffold built for AI-assisted development. The structure, documentation, and workflow are designed so a coding agent can open the repo, read a spec, implement a task, run the checks, and open a pull request — without needing a long custom prompt each time.

---

## Stack

| | |
|---|---|
| Language | Python 3.13 |
| Framework | Django + Django REST Framework |
| Database | PostgreSQL |
| Queue | Celery + Redis |
| Packaging | uv |
| Testing | pytest |
| Linting | Ruff |

---

## Quick Start

```bash
git clone <this-repo> myproject
cd myproject
cp .env.example .env       # set SECRET_KEY and DATABASE_URL
docker compose up
```

Visit `http://localhost:8000/health/` — you should see `{"status": "ok"}`.

**Without Docker:**
```bash
uv sync
uv run python src/manage.py migrate
uv run python src/manage.py runserver
```

---

## How to Start a New Project

1. Clone this repo (or use it as a GitHub template).
2. Find and replace `myproject` → your project name in `pyproject.toml`, `.env.example`, and `docker-compose.yml`.
3. Update `README.md`, `AGENTS.md`, and `ARCHITECTURE.md` with your project context.
4. Generate a fresh secret key:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
5. Run `docker compose up` and verify `/health/` returns 200.

---

## The AI-Native Development Workflow

This is the core of the repo. Every feature follows this cycle:

```
1. Write a spec        →  specs/active/my-feature.md
2. Break into tasks    →  tasks/TASK-001-my-feature.md
                          tasks/TASK-002-my-feature.md
3. Agent implements    →  reads AGENTS.md + spec → implements → tests
4. Verify              →  pytest  ·  ruff check .  ·  manage.py check
5. Open a PR           →  small, focused, reviewable
6. Archive the spec    →  specs/active/ → specs/completed/
```

### Why specs first?

A vague task like *"implement user registration"* gives an agent too much to infer. A spec defines the contract — what gets built, what the API looks like, and what done means — before a single line of code is written.

### Step 1 — Write a spec

Copy `specs/template.md` to `specs/active/` and fill it in:

```markdown
# User Registration

## Status
Active

## Goal
Allow new users to create an account with email and password.

## User Story
As a visitor,
I want to register with my email and password
so that I can access the platform.

## Requirements
- Email must be unique.
- Password must meet Django's default validators.
- Returns a session token on success.

## API
POST /api/v1/users/register/

## Acceptance Criteria
- New user is created and returned with HTTP 201.
- Duplicate email returns HTTP 400.
- Weak password returns HTTP 400 with field errors.
- Tests cover all three cases.

## Out of Scope
- Social login.
- Email verification.
```

### Step 2 — Break into small tasks

One spec → multiple small tasks. Each task is independently implementable and testable.

```
tasks/
  TASK-001-user-model.md
  TASK-002-registration-service.md
  TASK-003-registration-api.md
```

Copy `tasks/template.md` and fill it in:

```markdown
# TASK-002 — Registration Service

## Related Specification
specs/active/user-registration.md

## Objective
Implement the create_user() service function with all validation.

## Files Expected
src/apps/users/services.py
src/apps/users/tests/test_services.py

## Acceptance Criteria
- Duplicate email raises ValidationError.
- Weak password raises ValidationError.
- Valid input creates and returns a User instance.
- Tests pass.

## Do Not
- Modify URL routing.
- Touch the view or serializer.
```

### Step 3 — Agent implements

A coding agent reads `AGENTS.md` first (the operating manual), then the spec, then the task. It knows the architecture rules, the commands to run, and what "done" means — without you writing a custom prompt.

### Step 4 — Verify

The agent runs all three checks before declaring the task complete:

```bash
uv run pytest                          # tests must pass
uv run ruff check .                    # lint must pass
uv run python src/manage.py check      # Django system checks must pass
```

---

## Adding a New App

```bash
# 1. Create the app
mkdir -p src/apps/myapp/tests
touch src/apps/myapp/{__init__.py,apps.py,models.py,selectors.py,services.py,serializers.py,views.py,urls.py,admin.py}
touch src/apps/myapp/migrations/__init__.py
touch src/apps/myapp/tests/{__init__.py,test_models.py,test_services.py,test_views.py}
```

```python
# 2. Register in INSTALLED_APPS — src/config/settings/base.py
"apps.myapp",

# 3. Register routes — src/config/api_v1.py
path("myapp/", include("apps.myapp.urls")),
```

---

## Project Structure

```
├── src/
│   ├── manage.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py         # shared settings, env-driven
│   │   │   ├── local.py        # dev overrides
│   │   │   └── production.py   # create this before deploying
│   │   ├── api_v1.py           # all /api/v1/ routes
│   │   └── urls.py
│   └── apps/
│       ├── health/             # health check — keep this
│       └── <your-domain>/      # add your apps here
│
├── docs/
│   ├── architecture/           # how the system is designed
│   ├── decisions/              # ADRs — why we chose X
│   ├── features/               # feature-level docs
│   └── deployment/             # local, staging, production guides
│
├── specs/
│   ├── active/                 # in-progress specs
│   ├── completed/              # archived after merge
│   └── template.md             ← copy this to start a spec
│
├── tasks/
│   └── template.md             ← copy this to create a task
│
├── AGENTS.md                   ← agent operating manual (read first)
├── ARCHITECTURE.md             ← full system design and layer contracts
└── docker-compose.yml
```

---

## Key Commands

```bash
uv run python src/manage.py runserver        # dev server
uv run pytest                                # run all tests
uv run ruff check .                          # lint
uv run ruff format .                         # format
uv run python src/manage.py check            # Django system checks
uv run python src/manage.py makemigrations <app>
uv run python src/manage.py migrate
```

---

## Environment Variables

| Variable | Required | Default | Notes |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | Fails at startup if missing |
| `DATABASE_URL` | No | SQLite | Parsed by dj-database-url |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Celery broker |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated |
| `CORS_ALLOWED_ORIGINS` | No | `""` | Comma-separated |
| `DEBUG` | No | `False` | Set `True` for local dev |

---

## Definition of Done

A task is complete only when all of these pass:

- [ ] Acceptance criteria from the spec are satisfied
- [ ] Tests are added for new behavior
- [ ] `uv run pytest` passes
- [ ] `uv run ruff check .` passes
- [ ] `uv run python src/manage.py check` passes
- [ ] Documentation updated if architecture changed

---

## Contributing

1. Read `AGENTS.md` and `ARCHITECTURE.md` first.
2. Write a spec in `specs/active/` before implementing anything.
3. Keep business logic in services, not views.
4. Add tests for every new behavior.
5. All checks must pass before opening a PR.

---

## License

MIT — see [LICENSE](LICENSE).
