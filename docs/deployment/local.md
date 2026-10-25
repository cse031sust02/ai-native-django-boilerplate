# Local Development

## Prerequisites

- Docker and Docker Compose
- (Optional) uv — for running commands outside Docker

## Start Everything

```bash
docker compose up
```

This starts PostgreSQL, Redis, and Django at `http://localhost:8000`.
Migrations run automatically on startup.

## Useful Commands

```bash
# Start in background
docker compose up -d

# View logs
docker compose logs -f web

# Run a management command
docker compose exec web python src/manage.py createsuperuser

# Run tests
docker compose exec web pytest

# Stop
docker compose down

# Stop and remove volumes (wipe the database)
docker compose down -v
```

## Environment

Copy `.env.example` to `.env` and adjust values as needed.
The default `.env` already has working dev values.
