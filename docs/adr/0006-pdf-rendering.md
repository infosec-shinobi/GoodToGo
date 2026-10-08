# ADR 0006: PDF Rendering Approach

Status: Accepted for MVP 0 architecture  
Date: 2026-10-08

## Context

The product needs printable workbooks, take-home lists, and eventually audience-specific
exports. Early MVPs should stay simple and runnable without introducing a separate PDF
service before export policies and authorization are implemented.

## Decision

Use shared HTML templates and print CSS for MVP 1 browser print and save-to-PDF flows.
Defer server-side PDF rendering until audience-specific exports require controlled,
repeatable output.

When server-side rendering is introduced, select a renderer that:

- Runs inside the application deployment without third-party network calls.
- Uses already-authorized export models rather than querying arbitrary records while
  rendering.
- Supports deterministic headers, footers, generation timestamps, and source appendices.
- Can be tested in CI for basic output generation.
- Does not retain temporary plaintext exports beyond the request lifecycle.

## Consequences

- MVP 1 relies on browser print behavior and documents manual responsive/print QA.
- MVP 5 will need a dedicated renderer decision before full survival-package generation.
- Export policy and authorization boundaries remain more important than renderer choice.
