# Authentication

_Document the authentication approach for your project here._

## Options

Common patterns for Django REST APIs:

- **Session authentication** — built into DRF, good for browser clients.
- **JWT** — stateless tokens, good for mobile/SPA clients. Consider `djangorestframework-simplejwt`.
- **OAuth / Social login** — Google, GitHub, etc. Consider `django-allauth`.
- **API keys** — for service-to-service calls.

## Current Setup

The boilerplate ships with `SessionAuthentication` as the default in `REST_FRAMEWORK` settings. Replace or extend this when you add your auth implementation.

## Spec

Write a feature spec at `specs/active/authentication.md` before implementing.
