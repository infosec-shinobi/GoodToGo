# Roadmap

Status: Active roadmap  
Current milestone: MVP 1: Private “death party” workbook  
Last status review: 2026-10-03  
Delivery style: Small vertical MVPs with a runnable application after each milestone

Status legend:

- Done: exit criteria satisfied and release notes/deferred work recorded
- Mostly complete: implementation exists, but review, validation, or decisions remain
- In progress: active implementation has started and some scoped behavior works
- Not started: no user-facing implementation yet
- Blocked: waiting on a required external decision or review

## Definition of done for every MVP

- User-visible behavior documented
- Authorization and privacy impact reviewed
- Tests added and passing
- Database changes have reviewed migrations
- Content changes have pack-version impact assessed
- Logs contain no sensitive values
- Backup and export impact reviewed
- Accessibility checked with keyboard and automated tooling
- Release and rollback notes written
- Deferred work listed explicitly

## MVP 0: Foundation and content model

Status: Mostly complete; pending product, legal/content, authentication, encryption,
and PDF-renderer decisions.

Goal: Create a repository that agents can safely extend and a content model that can
drive web and print outputs.

Included in this starter:

- FastAPI and Jinja2 application
- Docker Compose and PostgreSQL target
- Versioned YAML workbook and resource catalog
- Persistent entity draft
- Per-user preference model
- Theme and color-scheme prototype
- Security headers
- Architecture, requirements, content, data, security, export, and recovery docs
- Agent instructions and tests

Remaining tasks:

- Review working product name
- Validate initial content with an Ohio estate attorney
- Validate medical content with an appropriate clinician or advance-care specialist
- Decide authentication approach
- Approve encryption ADR
- Decide PDF renderer

Exit criteria:

- Product boundary accepted
- Content taxonomy accepted
- No raw-secret fields
- Initial threat model reviewed

## MVP 1: Private “death party” workbook

Status: In progress; starter implementation exists for the private workbook,
section navigation, time estimates, safe notes fields, browser-local answers,
generated take-home tasks, public catalog API, clear-session, theme controls, and
browser print views.

Goal: Let a family member complete a useful guided session without an account or
server-side answer retention.

### 1.1 Workbook experience

- Done: Add section navigation and time estimates
- Done: Add safe notes fields where appropriate
- Add conditional applicability questions
- Add “needs professional help” to generated tasks
- Support save-off by default and explicit local-device save
- Add clear inactivity and data-loss behavior
- Add responsive Android and desktop testing

### 1.2 Take-home list

- Allow task selection and priority adjustment
- Add responsible person and target-date fields locally
- Provide print view with notes space
- Provide source appendix and link verification metadata
- Add blank take-home list for paper participants

### 1.3 Private resume and export

- Design an interoperable encrypted resume-file format
- Add password strength and loss warnings
- Export and import without server processing
- Produce blank and completed workbook PDFs through browser print
- Add no-answer-network browser tests

Exit criteria:

- A participant can complete the flow, leave with a task list, and clear the device
- Network test proves workbook answers never leave the browser
- Print output is usable in color and black-and-white

## MVP 2: Persistent households and user preferences

Status: Not started; data-model scaffolding exists, but authentication, sessions,
household CRUD, authorization, persisted preferences, and persistent workbook behavior
are not implemented.

Goal: Allow spouses and trusted household members to collaborate over time.

### 2.1 Authentication

- Local account registration behind an administrator setting
- Secure password hashing
- Email verification and recovery design
- TOTP or passkeys
- Secure session and CSRF implementation
- Optional OIDC design for later activation

### 2.2 Household tenancy

- Create household
- Invite, accept, revoke, and leave
- Create subjects with and without logins
- Owner, contributor, viewer, delegate, and professional roles
- Central relationship-aware authorization service
- Cross-household isolation tests
- PostgreSQL row-level-security design

### 2.3 Settings

- Persist display mode, color scheme, timezone, and reduced motion per user
- Reconcile cached theme with authenticated preference
- Add settings API and audit relevant security-setting changes
- Test all schemes in light and dark modes for contrast

### 2.4 Persistent workbook

- Save responses, readiness states, review dates, and notes
- Generate durable tasks from response changes
- Dashboard critical gaps and stale sections
- Keep content-pack version with answers
- Support import from a private encrypted resume file after explicit confirmation

Exit criteria:

- Two users collaborate within one household
- One user belongs to two isolated households
- Theme preferences follow authenticated users
- Authorization regression suite passes

## MVP 3: Domain records and document locations

Status: Not started; record, document, task, and household model scaffolding exists,
but user-facing inventory CRUD and authorization-backed workflows are not implemented.

Goal: Move beyond checklist answers into a maintainable household inventory.

- People and role records
- Legal document status and authoritative locations
- Financial account and liability metadata
- Insurance policies
- Utilities and recurring services
- Digital account and device records
- Household systems and vendors
- Desired disposition and communication instructions
- Record ownership and visibility
- Last verified and next review dates
- Location-only document support

Exit criteria:

- Core records can be created, updated, reviewed, and exported
- Joint and individual ownership work correctly
- No credential secrets are accepted

## MVP 4: Encrypted documents and security hardening

Status: Not started; encryption-related fields exist in the draft model, but key
lifecycle, upload handling, encrypted storage, audit behavior, and hardening work are
not implemented.

Goal: Safely support optional document copies.

- Finalize per-household envelope encryption
- Key generation, wrapping, rotation, backup, and recovery
- Storage adapter and non-web-root objects
- Upload allowlist, type and signature validation, and size limits
- Quarantine and optional local malware scanning
- Authorized streaming downloads
- Document integrity hashes
- Append-only audit events
- Step-up authentication for sensitive export and security actions
- Security review and dependency scanning

Exit criteria:

- Key rotation and restored-backup decryption pass
- Cross-household document tests pass
- Malicious and oversized upload tests pass
- Limitations of server-side encryption are disclosed

## MVP 5: Audience-specific exports and survival package

Status: Not started; browser print views exist for the private workbook and take-home
list, but policy-driven exports and offline survival packages are not implemented.

Goal: Create trustworthy handoff materials independent of the app.

- Export-policy engine
- Emergency and incapacity binder
- Household continuity guide
- Executor and survivor binder
- Digital fiduciary guide
- Redaction preview and confirmation
- Full encrypted archive
- Static offline HTML index
- Versioned JSON, original documents, and manifest
- Temporary-file cleanup and audit
- Annual trusted-person recovery exercise

Exit criteria:

- Authorized recipients receive only intended content
- Export works in an isolated offline environment
- A nontechnical tester can start from `START-HERE.pdf`

## MVP 6: Review, reminders, and life events

Status: Not started.

Goal: Keep plans current.

- Annual and custom review schedules
- Marriage, divorce, birth, death, move, health, employment, and asset-change triggers
- Beneficiary and account-ownership review
- Role reconfirmation
- Official-link stale checks
- Backup and survival-package age warnings
- Email notifications with no sensitive content
- Dashboard focused on critical and stale items

## MVP 7: Survivor mode

Status: Not started.

Goal: Guide an authorized survivor through the practical aftermath.

- First hours and days
- First weeks
- Following months
- Estate closure and surviving-household updates
- State and federal resources
- Provider-specific digital account guides
- Task assignment and evidence
- Professional-review and legal-safety gate

This mode must never instruct someone to impersonate the deceased, use credentials
without authority, distribute estate property, or pay debts personally without proper
authority and guidance.

## MVP 8: Jurisdiction packs and trusted professional sharing

Status: Not started.

- Ohio pack reviewed and release-managed
- Additional state packs
- Time-limited professional access
- Expiring redacted report links
- Content signature and trusted-publisher model
- Source update and retirement workflow

## Future ideas

- Anonymous group-session facilitator dashboard
- Printable facilitator kit
- Local-only assisted document classification
- Read-only Home Lifecycle Record integration
- Read-only password-manager item-location validation without retrieving secrets
- Native mobile wrappers only if PWA limitations become material
