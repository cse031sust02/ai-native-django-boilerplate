# ADR 001 — Use PostgreSQL

## Status
Accepted

## Context

The project needs a relational database for structured data. We need ACID guarantees, JSON support for flexible schema fields, and mature Django integration.

## Decision

Use PostgreSQL 16 as the primary database.

## Reasons

- Best-supported database in the Django ecosystem.
- Native JSONB column type for semi-structured data without a separate document store.
- `pgvector` extension available if vector storage is needed in the future.
- Supported by all major managed hosting providers (RDS, Cloud SQL, Supabase, Neon).

## Consequences

- Requires a running PostgreSQL instance (handled via Docker in dev, managed service in production).
- Migrations must be tested against Postgres, not SQLite.
