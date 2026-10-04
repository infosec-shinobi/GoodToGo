# ADR 0002: Use a Versioned Content Catalog

Status: Accepted for scaffold  
Date: 2026-09-11

## Context

The web workbook, blank workbook, take-home list, jurisdiction guidance, and persistent
workflow need the same questions and sources. Hard-coded copies would drift.

## Decision

Store sections, questions, help text, review cadence, task rules, and resource references
in a versioned catalog. Store official guides in a separately versioned resource file.

Use stable IDs. Persist the content-pack version with household and answer data.

## Consequences

- Content changes require validation and version review.
- Multiple renderers can share the same source.
- Jurisdiction packs can extend the core model.
- Professional content review can occur without rewriting application routes.

