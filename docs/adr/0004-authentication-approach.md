# ADR 0004: Authentication Approach

Status: Accepted for MVP 0 architecture  
Date: 2026-10-08

## Context

MVP 0 needs a clear direction for future persistent households without adding a partial
authentication system before household authorization exists. Authentication must support
self-hosted deployments, household collaboration, and a future path to stronger factors.

## Decision

Use local application accounts for the first persistent-household MVP, with the following
requirements:

- Argon2id password hashing for local passwords.
- Secure, HTTP-only, same-site session cookies.
- CSRF protection for browser state changes.
- Session rotation at login and privilege changes.
- Rate limiting that does not log submitted credentials.
- MFA support before recommending general internet exposure.
- Optional OIDC support as a later integration, not an MVP 2 dependency.

Instance administrators remain separate from application household membership. Operating
the deployment does not grant household-content access in the application authorization
model.

## Consequences

- MVP 1 stays account-free and does not need authentication.
- MVP 2 can implement local registration behind an administrator setting.
- OIDC can be added after the local account and authorization model are proven.
- Account recovery must be designed so it does not bypass household encryption.
