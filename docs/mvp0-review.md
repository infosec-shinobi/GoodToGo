# MVP 0 Review Record

Status: Complete for personal-project use  
Review date: 2026-10-08

## Product Boundary

Accepted for MVP 0.

GoodToGo is an organizer and continuity tool. It does not create legal documents,
provide personalized legal, tax, financial, or medical advice, store raw credentials, or
replace qualified professional review.

The working product name is accepted as `GoodToGo` for the current repository and MVP 1
workbook experience.

## Content Taxonomy

Accepted for MVP 0 implementation.

The initial taxonomy in `docs/content-inventory.md` and the versioned workbook pack in
`app/content/core_us/workbook.yaml` are suitable for building the scaffold, private
workbook, generated task list, and print views.

The content taxonomy is not professionally validated. The app should continue to call out
where legal, medical, tax, or financial guidance should be obtained instead of presenting
the workbook as professional advice.

## Security And Privacy Review

Accepted for MVP 0 scaffold.

The initial threat model in `docs/security-threat-model.md` defines the protected assets,
trust boundaries, principal threats, and required controls for later persistent use.

MVP 0 and MVP 1 preserve the private-session boundary: no answer submission endpoint, no
analytics, opt-in browser local storage only, and no raw-secret fields.

## Raw-Secret Field Review

Accepted for MVP 0 scaffold.

The content model and current workbook ask for credential locators, recovery topology, and
setup status. They do not ask for raw passwords, MFA seeds, recovery codes, safe
combinations, or private cryptographic keys.

ADR 0003 records this as an architectural rule.

## Architecture Decisions Closed For MVP 0

- ADR 0001: Separate private and persistent modes
- ADR 0002: Use a versioned content catalog
- ADR 0003: Do not store raw credentials
- ADR 0004: Authentication approach
- ADR 0005: Persistent encryption approach
- ADR 0006: PDF rendering approach

## Professional Guidance Boundary

For this personal project, MVP 0 does not require attorney or clinician validation before
continued development. Instead, the project documents and user-facing workbook should call
out when professional guidance is appropriate.

See `docs/professional-guidance.md`.

Do not claim the content is legally reviewed, medically reviewed, or jurisdiction-accurate
unless that external review happens later.
