# ADR 0005: Persistent Encryption Approach

Status: Accepted for MVP 0 architecture  
Date: 2026-10-08

## Context

Persistent household records and documents will contain sensitive legal, medical,
financial, household, and digital-life metadata. The application needs a documented
encryption direction before persistent production use, while private sessions must remain
browser-local and avoid server-side answer storage.

## Decision

Use application-managed per-household envelope encryption for sensitive persistent
payloads and uploaded documents:

- Generate a random data-encryption key for each household.
- Encrypt sensitive record payloads and files with authenticated encryption.
- Wrap each household key with a versioned instance key-encryption key.
- Store wrapped household keys with household encryption metadata.
- Keep instance key material outside the database.
- Support key rotation and restored-backup decryption before production use.

Do not claim zero-knowledge security. A person controlling the running application and key
material may be technically capable of accessing decrypted persistent content.

## Consequences

- MVP 1 private-session answers remain out of server persistence entirely.
- MVP 2 can create household tenancy before encrypted document upload exists.
- MVP 4 must implement key lifecycle, rotation, backup, restore, and disclosure UI before
  persistent document security is considered complete.
- Backup documentation must cover database, documents, content-pack versions, encryption
  metadata, and separately protected key material.
