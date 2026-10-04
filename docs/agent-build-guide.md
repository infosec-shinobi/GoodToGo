# Agent Build Guide

This repository is intended for incremental development with coding agents. Give an
agent one bounded vertical slice at a time.

## Required reading for every agent

- `AGENTS.md`
- `README.md`
- `docs/product-requirements.md`
- `docs/architecture.md`
- `docs/security-threat-model.md`
- The relevant MVP in `docs/roadmap.md`

## Source-of-truth hierarchy

1. `AGENTS.md` safety and engineering rules
2. Accepted ADRs in `docs/adr/`
3. Product requirements
4. Architecture and threat model
5. Current roadmap MVP
6. Versioned content catalog
7. Existing implementation and tests

If these conflict, stop and document the conflict rather than silently choosing.

## Standard agent prompt

```text
You are implementing one vertical slice in the GoodToGo repository.

Read AGENTS.md and the documents it requires before changing code. Work only on the
bounded task below. Preserve the private-session no-answer-network invariant, never add
raw-secret fields, and scope every persistent resource to a household with centralized
authorization.

Task:
<one bounded task>

Acceptance criteria:
<observable behavior and tests>

Before finishing:
1. Run the relevant tests and ruff check.
2. Review privacy, authorization, logging, schema, content-version, and export impact.
3. Update documentation and migrations when applicable.
4. Summarize user-visible result, security impact, tests, and deferred work.
```

## Recommended first agent tasks

### Task 1: Strengthen catalog validation

Acceptance criteria:

- Validate stable ID format.
- Validate semantic content-pack version.
- Require HTTPS official resources except explicit development fixtures.
- Detect duplicate resource IDs.
- Validate task priority and answer values.
- Add focused tests and useful startup errors.

### Task 2: Add private-session browser tests

Acceptance criteria:

- Use Playwright in a dedicated test profile.
- Complete sample questions and generate tasks.
- Confirm no request contains question IDs paired with answer values.
- Confirm local storage remains empty until opt-in.
- Confirm Clear removes answers.
- Test Android-sized viewport and keyboard interaction.

### Task 3: Improve printable take-home output

Acceptance criteria:

- Add participant-supplied task owner and target date locally.
- Add print header, generation date, and content-pack version.
- Show full guide URLs in print.
- Keep tasks together across page breaks.
- Verify black-and-white output.

### Task 4: Decide authentication architecture

Deliver an ADR only. Compare:

- Local authentication with passkeys and TOTP
- OIDC-only
- Local plus optional OIDC

Include account recovery, self-hosted email limitations, spouse access, instance admin
separation, and migration implications. Do not implement until the ADR is accepted.

### Task 5: Implement per-user settings vertical slice

Prerequisite: accepted authentication ADR and authenticated request identity.

Acceptance criteria:

- Read and update the current user's `UserPreference` only.
- Validate allowed mode and scheme values.
- Reconcile cached and server values without theme flash.
- Add authorization and API tests.
- Test system, light, and dark with every color scheme.
- Add reduced-motion handling.

### Task 6: Implement household creation and membership

Acceptance criteria:

- Create a household and owner membership atomically.
- Invite and accept with short-lived, single-use tokens.
- Revoke access immediately.
- Prevent role escalation and cross-household enumeration.
- Add audit events without email addresses or token values.
- Add database migration and authorization tests.

## How to split work safely

Good parallel boundaries:

- Content research versus application code
- Print CSS versus database schema
- Threat-model review versus UI accessibility review
- Unit tests for independent services

Avoid parallel changes to:

- The same migration chain
- Authorization policy
- Encryption formats
- Content-pack versioning semantics
- The same templates and CSS variables

## Review checklist for agent-generated changes

- Does the feature collect more data than necessary?
- Could an answer reach the server in private mode?
- Can a valid user alter a household or object ID to access another record?
- Does an instance administrator gain accidental application permissions?
- Are any secrets, payloads, tokens, or filenames logged?
- Does the change alter export contents?
- Can a new field leak into every export by default?
- Does a changed question require a content-pack version change?
- Is a schema migration reversible and safe?
- Can recovery still work if the original administrator is unavailable?

