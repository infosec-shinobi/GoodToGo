# ADR 0003: Do Not Store Raw Credentials

Status: Accepted for scaffold  
Date: 2026-09-11

## Context

An affairs organizer already concentrates high-risk information. Duplicating passwords,
MFA seeds, recovery codes, private keys, and safe combinations would increase impact and
create a second credential lifecycle.

## Decision

Store credential locators, recovery topology, responsible people, and provider legacy
configuration status. Do not accept raw credentials or recovery secrets.

Examples:

- Good: `Bitwarden > Family Emergency > Home router`
- Good: `Printed recovery kit in attorney-held envelope`
- Prohibited: router password
- Prohibited: Bitwarden master password
- Prohibited: authenticator seed or recovery code

## Consequences

- A separate password manager or sealed recovery kit remains required.
- Exports are useful maps rather than complete credential vaults.
- Future password-manager integration must not retrieve secrets.

