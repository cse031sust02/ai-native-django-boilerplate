# ADR 002 — Use Celery for Background Jobs

## Status
Accepted

## Context

Several platform operations must not block the HTTP request cycle: sending emails, generating PDF reports, triggering LLM calls, and indexing uploaded documents.

## Decision

Use Celery with Redis as the broker for all background task processing.

## Reasons

- Mature, well-documented, and widely used in the Django ecosystem.
- Supports task retries, rate limiting, and priority queues out of the box.
- Redis (already used for caching) doubles as the broker, avoiding an extra service.
- Easy to scale workers horizontally without changing application code.

## Consequences

- Workers must be kept running alongside the web process.
- Tasks must be designed to be idempotent (safe to retry).
