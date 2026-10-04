# Product Requirements

Status: Draft for review  
Working product name: GoodToGo  
Initial jurisdiction: United States core with an Ohio content pack

## Product statement

GoodToGo helps a person or household decide, organize, locate, share, and
maintain the information trusted people may need during incapacity or after death.
It combines traditional affairs-in-order planning with digital-life and household
continuity guidance.

The product is an organizer and readiness system. It is not a law firm, medical
provider, tax advisor, financial advisor, password manager, or legally binding
document generator.

## Outcomes

A prepared household should be able to answer:

1. Who is responsible for each decision or task?
2. Has that person agreed and been legally appointed where needed?
3. What authoritative documents exist, and where are the signed originals?
4. What assets, debts, policies, benefits, accounts, systems, and obligations exist?
5. What should happen to each physical and digital asset?
6. Can the household continue operating during incapacity?
7. Can survivors begin without depending on the unavailable person or running app?
8. When was each answer last verified?

## Users and modes

### Private-session participant

- Uses the workbook without an account.
- Answers stay in browser memory unless device storage is explicitly enabled.
- Receives a prioritized take-home list with setup guides.
- Can print a blank or completed workbook and task list.
- Will later be able to create an encrypted resume file.

### Persistent household member

- Belongs to one or more households.
- May document themselves and other household subjects.
- Collaborates according to household membership and per-record grants.
- Has personal theme, color scheme, timezone, and accessibility preferences.
- Can produce authorized, audience-specific exports.

### Trusted delegate

- Receives only explicitly granted information.
- May act as health care agent, financial agent, executor, trustee, digital fiduciary,
  caregiver, or another named role.
- Does not receive broad household access merely because a role label exists.

### Temporary professional

- May receive time-limited access to selected records or an export.
- Intended for an attorney, accountant, financial advisor, social worker, or clinician.
- Access is revocable and audited.

### Instance administrator

- Operates the application and infrastructure.
- Manages availability and configuration.
- Does not automatically receive application-level household permissions.
- Must be told honestly that an operator with server and encryption-key access may be
  technically capable of accessing persistent plaintext while the app is running.

## Core functional requirements

### Guided readiness

- Organize questions into approachable sections with time estimates.
- Support Ready, In progress, Not started, Not sure, and Not applicable.
- Support “needs professional help” as a task state in persistent mode.
- Explain why each question matters without giving personalized legal advice.
- Show source, jurisdiction, content-pack version, and review date for guidance.
- Generate follow-up tasks from incomplete or uncertain answers.
- Sort take-home tasks by urgency, then allow the user to reorder them.

### Persistent collaboration

- A user can belong to multiple households.
- A household can include multiple planning subjects.
- A subject may or may not have a login.
- Records may be individual, joint, or household-owned.
- Visibility is independent from ownership.
- Invites, grants, revocation, viewing, changes, and exports are auditable.

### Documents and locations

- Support “document exists at this location” without requiring upload.
- Support encrypted uploads after the document-security MVP.
- Track signed-original location separately from uploaded-copy location.
- Track executed date, expiration, last review, and responsible professional.
- Never imply that an uploaded copy replaces an authoritative original.

### Digital life

- Record service, account owner, identifying email, purpose, value, credential
  locator, MFA method, recovery path, provider legacy feature, and desired disposition.
- Link to official setup and survivor guides.
- Never store raw passwords, passcodes, MFA seeds, recovery codes, safe combinations,
  or private cryptographic keys.
- Treat primary email, mobile number, password manager, and MFA devices as an identity
  recovery chain rather than unrelated accounts.

### Household continuity

- Cover utilities, recurring bills, insurance, childcare, pets, vehicles, emergency
  shutoffs, vendors, security systems, home networking, smart home, computers, storage,
  backups, domains, and self-hosted services.
- Separate a short emergency operations page from detailed system documentation.

### User settings

- Every authenticated user has their own preferences.
- Theme modes: system, light, and dark.
- Initial color schemes: ocean, forest, ember, plum, and slate.
- Cache theme values locally to prevent a flash of the wrong theme.
- Sync authenticated changes to `user_preferences`.
- Preserve accessible contrast and reduced-motion support.

### Exports

- Blank printable workbook
- Personalized take-home task list
- Emergency and incapacity binder
- Household continuity guide
- Executor and survivor binder
- Digital fiduciary guide
- Full encrypted survival package
- Machine-readable, versioned JSON and manifest

## Nonfunctional requirements

- Mobile-first responsive use
- Keyboard and screen-reader accessibility
- WCAG AA color contrast
- PostgreSQL production data store
- Docker Compose deployment
- No external network dependency for core persistent operation
- No third-party analytics by default
- Export independent of a running application
- Versioned content and schema migrations
- Tested household isolation and object-level authorization
- Backups with a documented and rehearsed restore procedure

## Explicitly out of scope for early MVPs

- Creating or electronically signing wills, powers of attorney, trusts, or medical orders
- Personalized legal, tax, financial, or medical recommendations
- Bank-account aggregation
- Credential vaulting
- Automatic declaration that a user is deceased
- Automatic break-glass release based only on inactivity
- AI extraction from private documents
- Public SaaS operation
- Mobile native applications

## Product measures

Avoid a simplistic “percentage ready for death.” More useful measures include:

- Critical tasks remaining
- Sections reviewed in the last 12 months
- Responsible roles confirmed
- Beneficiary and ownership reviews current
- Digital identity recovery chain tested
- Offline survival package current
- Trusted-person recovery test completed

