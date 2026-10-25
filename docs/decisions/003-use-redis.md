# ADR 003 — Use Redis

## Status
Accepted

## Context

The platform needs fast in-memory storage for caching, session data, Celery task queuing, and JWT token denylisting.

## Decision

Use Redis 7 as the shared in-memory store for caching and as the Celery broker/result backend.

## Reasons

- Single service covers multiple use cases: cache, queue broker, result store, denylist.
- Django has first-class Redis cache backend support.
- Sub-millisecond read/write latency for hot data (rate limits, session lookups).
- Widely supported on managed platforms (ElastiCache, Upstash, Redis Cloud).

## Consequences

- Redis is a required service in every environment (local, staging, production).
- Data in Redis is ephemeral by default — do not store anything that cannot be reconstructed from Postgres.
