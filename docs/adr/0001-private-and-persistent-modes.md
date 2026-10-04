# ADR 0001: Separate Private and Persistent Modes

Status: Accepted for scaffold  
Date: 2026-09-11

## Context

Temporary server accounts do not fully solve privacy because answers may remain in logs,
snapshots, and backups. Multi-household persistence is still valuable for spouses and
trusted collaborators.

## Decision

Provide two distinct modes:

- Private sessions process answers in the browser and do not transmit them.
- Persistent households store authorized, encrypted information on the server.

The public content catalog and display code may be shared, but state handling and privacy
claims must remain distinct.

## Consequences

- Private mode requires more client-side code than the persistent Jinja and HTMX UI.
- Encrypted resume files require a separate design.
- Temporary server workspaces are unnecessary for the initial product.
- The product can honestly offer a stronger privacy option to guests.

