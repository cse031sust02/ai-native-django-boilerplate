# Authentication Architecture

## Approach

JWT-based authentication via Django REST Framework.

## Flow

```
POST /api/auth/login/
        |
        v
  Validate credentials
        |
        v
  Issue access + refresh tokens
        |
        v
  Client stores tokens, sends Authorization: Bearer <token> on each request
```

## Token Strategy

- Access token: short-lived (e.g. 15 min)
- Refresh token: long-lived (e.g. 7 days)
- Tokens are stateless; invalidation handled via a denylist in Redis.

## Password Auth

- Django's built-in `authenticate()` and `check_password()`.
- Passwords hashed with PBKDF2.

## Security Rules

- Never log access tokens.
- Secrets and client credentials come from environment variables only.
- Production tokens must use HTTPS only.
