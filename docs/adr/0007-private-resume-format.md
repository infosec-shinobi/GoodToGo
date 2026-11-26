# ADR 0007: Browser-only encrypted private resume files

Status: Accepted for MVP 1 prototype; independent cryptographic review pending  
Date: 2026-11-05

## Context

MVP 1.3 needs portable private-session recovery without sending answers or passphrases
to the server. Recovery must not depend on a live GoodToGo installation. Web Crypto
provides authenticated encryption but not a memory-hard password KDF. A native-only
PBKDF2 design would not satisfy the threat model's memory-hard KDF requirement.

## Decision

Use the documented [v1 resume envelope](../private-resume-format.md): UTF-8 JSON,
scrypt (RFC 7914, N=131072, r=8, p=1, 32-byte output, random 16-byte salt) and Web
Crypto AES-256-GCM (random 12-byte IV, 128-bit tag, fixed format/version AAD).
These are standard primitives; the application defines only the envelope and payload
schema, not a new cipher or KDF. Do not advertise this as a standardized archive format
readable by arbitrary ZIP/password-manager tools.

Vendor the unchanged MIT-licensed `scrypt-js@3.0.1` implementation locally, with
provenance, SHA-256, and RFC known-answer tests. A short-lived local worker performs
the KDF when available. The already-loaded async implementation is the fallback for
offline operation or unavailable workers, using exactly the same parameters. Never
fall back to weaker encryption or a plaintext download. Web Crypto requires HTTPS or
localhost; unsupported contexts disable resume actions while leaving the workbook usable.

Validate size, format, fixed parameters, encoding, authenticated payload, matching pack
ID/version, and all answer/task fields before replacing any session state. Require
explicit replacement confirmation, keep failed imports non-destructive, and turn off
device saving on successful import. Clear-session aborts pending operations and prevents
late results from restoring cleared answers or triggering downloads.

Include an independent offline Python recovery tool using `hashlib.scrypt` and
`cryptography` AESGCM. Test both browser-to-Python recovery and Python-to-browser import.
Do not require the database, application imports, or server for that recovery tool.

## Consequences and limitations

- Derivation uses approximately 128 MiB plus overhead. Low-memory browsers may fail;
  async fallback can take tens of seconds. Never silently reduce the work factor.
- Minimum export passphrase length/repetition checks and advice to use random words
  are not entropy guarantees. No reset or recovery service exists. Files permit offline
  guessing, so passphrase quality matters.
- Neither passphrases nor keys are deliberately persisted. Best-effort byte clearing
  and worker termination do not guarantee erasure of JavaScript strings, library copies,
  browser heaps, swap, or crash dumps. Compromised browsers/hosts remain out of scope.
- Files reveal format, algorithm parameters, and approximate payload size, not answer
  or content-pack metadata. No compression is used.
- Exact pack-version matching prevents silent reinterpretation. Version migration is
  future work; preserve the matching application release or use offline recovery.
- Printing remains browser-managed under ADR 0006. PDFs/paper are plaintext outputs
  with retention warnings, distinct from encrypted resume-file downloads.
- Independent cryptographic review, physical-device memory/performance checks, and
  manual screen-reader/physical-print review remain release gates, not claimed complete.
