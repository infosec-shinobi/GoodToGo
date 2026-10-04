# AGENTS.md

These instructions apply to the entire repository.

## Before making changes

1. Read `README.md`, `docs/architecture.md`, `docs/product-requirements.md`,
   `docs/security-threat-model.md`, and `docs/roadmap.md`.
2. Check the current MVP boundary in `docs/roadmap.md`.
3. Treat `app/content/core_us/workbook.yaml` as versioned product content.
4. Record meaningful architectural changes in `docs/adr/`.

## Non-negotiable product rules

- This product organizes information; it does not create legal documents or give
  personalized legal, tax, financial, or medical advice.
- Private-session answers must remain in the browser. Do not add analytics,
  telemetry, server-side autosave, or API calls containing private-session answers.
- Do not store raw passwords, MFA seeds, recovery codes, private keys, or safe
  combinations. Store only credential locators and setup status.
- Every persistent resource must be scoped to a household and authorized for the
  current user on every request.
- Instance administrators do not automatically receive application-level access to
  household content.
- Export and recovery must work without the running application.
- User-visible guidance must include its source URL, jurisdiction, last-reviewed
  date, and content-pack version.
- Do not silently change the meaning of an existing workbook question. Version and
  migrate the content pack.

## Engineering expectations

- Use Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic, PostgreSQL, Jinja2, HTMX, and
  limited vanilla JavaScript.
- Prefer vertical slices that leave the application runnable.
- Add or update tests for behavior changes.
- Create Alembic migrations for persistent schema changes.
- Use UUIDs for externally addressable identifiers.
- Keep authorization policy in a central service or dependency, not scattered
  ad-hoc checks.
- Keep logs free of response bodies, record payloads, document contents, tokens,
  email addresses, and other sensitive data.
- Use CSS custom properties for themes and preserve WCAG AA contrast.
- Run `pytest` and `ruff check .` before marking work complete.

## Pull-request or handoff summary

Include:

- User-visible result
- Security and privacy impact
- Schema or content-pack migration impact
- Tests run
- Deferred work

