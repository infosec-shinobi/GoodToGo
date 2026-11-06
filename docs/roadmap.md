# Roadmap

Status: Active roadmap  
Current milestone: MVP 1: Private “death party” workbook  
Last status review: 2026-11-05
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

## Reference checklist coverage

The practical handoff ideas in
[potatoqualitee/eol-dr's checklist](https://github.com/potatoqualitee/eol-dr/blob/main/checklist.md)
were reviewed on 2026-11-05. The [coverage map](eol-dr-coverage.md) accounts for
each topic, its delivery milestone, and safety adaptations. This is a planning
reference, not professionally reviewed guidance or a claim of implemented coverage.
The current MVP 1 boundary is unchanged; the detailed inventory and survivor workflows
below are future work. New workbook questions require a versioned content-pack review.

## MVP 0: Foundation and content model

Status: Complete for personal-project use; professional validation not claimed.

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

- Done: Review working product name; accepted as GoodToGo for current MVP work
- Done: Legal and medical professional-guidance boundaries documented; see `docs/professional-guidance.md`
- Done: Decide authentication approach; see ADR 0004
- Done: Approve encryption ADR; see ADR 0005
- Done: Decide PDF renderer; see ADR 0006

Exit criteria:

- Done: Product boundary accepted; see `docs/mvp0-review.md`
- Done: Content taxonomy accepted for scaffold; see `docs/mvp0-review.md`
- Done: No raw-secret fields; see ADR 0003 and `docs/mvp0-review.md`
- Done: Initial threat model reviewed; see `docs/mvp0-review.md`

## MVP 1: Private “death party” workbook

Status: In progress; starter implementation exists for the private workbook,
section navigation, time estimates, safe notes fields, conditional applicability,
professional-help task flags, browser-local answers, inactivity auto-clear,
generated take-home tasks, public catalog API, clear-session, theme controls, and
browser print views.

Goal: Let a family member complete a useful guided session without an account or
server-side answer retention.

### 1.1 Workbook experience

- Done: Add section navigation and time estimates
- Done: Add safe notes fields where appropriate
- Done: Add conditional applicability questions
- Done: Add “needs professional help” to generated tasks
- Done: Support save-off by default and explicit local-device save
- Done: Add clear inactivity and data-loss behavior
- Done: Add responsive Android and desktop testing

### 1.2 Take-home list

- Done: Allow task selection and priority adjustment
- Done: Add responsible person and target-date fields locally
- Done: Provide print view with notes space
- Done: Provide source appendix and link verification metadata
- Done: Add blank take-home list for paper participants

Implementation and automated checks are complete. Physical print, real-browser
keyboard/screen-reader, and automated accessibility validation remain release checks;
see `docs/mvp1-2-review.md` for release, rollback, and deferred work.

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

### 3.1 People, notifications, wishes, and care

- Ordered notification contacts with preferred channels and a named notifier;
  distinguish private family/friend notifications from later public announcements
- Attorney, accountant, advisor, employer/benefits contacts, and trusted technical
  helpers, with confirmation of willingness and separate authority/access evidence
- Obituary inclusions/exclusions, preferred photos, service music/readings, and
  disposition preferences, distinct from legally authoritative instructions
- Pet veterinarian, food, medication, routines, current identification photos, and
  agreed primary/backup caregivers

### 3.2 Money coming in, money going out

- Income and deposit inventory, including royalties, sponsorships, advertising,
  creator/platform income, business receipts, pensions, and employer benefits
- Account purpose, ownership, insurance/benefit contacts, and professional-review
  status; retirement survivor benefits, dependent health-coverage continuity, and
  savings intended for grandchildren or other beneficiaries
- Payment dependency map: which account/card funds each bill, provider direct debits
  versus bank-scheduled bill pay, amount/frequency, renewal/contract/notice dates,
  and intended keep/cancel/transfer/review action
- Streaming, app-store and family subscriptions, recurring shipments, and cloud,
  hosting, domain, and CI/build-service costs, including spending urgency and helper
  or provider support contacts; do not assume family subscriptions are transferable
- Location of tax records and prior returns as discovery aids for missing income or
  accounts, with accountant review rather than financial or tax recommendations

### 3.3 Digital recovery, preservation, and disposition

- Primary/recovery/forwarded email relationships and shared operational uses such as
  delivery notices; phone/SIM/VoIP dependencies, authenticators, security-key and spare
  locations, recovery-kit locators, and provider emergency/legacy setup status
- Device retention and release prerequisites while recovery or data preservation is
  still needed; no universal one-year retention rule or guarantee that authenticator
  cloud restore recovers every account
- Per-service preserve/export/memorialize/transfer/cancel/delete wishes, subject to
  provider rules and legal authority; separately track personal profiles, business
  pages, communities, and sentimental digital material
- Cloud photos/documents and local/NAS backups: recognizable device/location labels,
  safe access locators, backup/restore-test status, export destinations, and a
  preservation check before closure, wiping, or disposal
- Domains, registrar/DNS/hosting and repository dependencies: renewal funding,
  intended recipient, support/helper contacts, and authorized transfer prerequisites
- Hardware recipients and disposition prerequisites, including verified preservation,
  media-appropriate sanitization, and vendor activation-lock/Find My release processes
- Nontechnical network and smart-home runbooks: identify equipment, safe restart order
  and wait times, outage checks, escalation contacts, Wi-Fi-change dependencies,
  essential services to retain, and a simpler replacement or shutdown plan
- Physical-security equipment, keys, and controlled-property contacts/locations;
  record only authorized access arrangements and credential locators, never PINs,
  combinations, security-question answers, or other recovery secrets

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
- A short, plain-language “start here” handoff: who to call first, what must keep
  working, what not to cancel/wipe yet, and where authoritative originals are located
- Separate nontechnical household instructions from a restricted technical appendix;
  include billing dependencies, preservation-before-disposal checks, and source metadata
- Printed-copy location, generated/reviewed dates, and a way to identify the current
  offline copy without putting passwords or recovery secrets in the application export

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
- Optional six-month print/recovery-kit review and reprint reminders, plus updates
  after device, MFA, helper, billing, network, or provider changes; track kit location
  and verification status, not kit secrets

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
- Notify designated people privately in the recorded order before public announcements;
  prepare a human checklist, not automatic messages or social-account posting
- Preserve needed phones, email, photos, documents, and backups before account closure
  or hardware disposal; hand off to the agreed technical helper when necessary
- Review keep/cancel/transfer actions against payment dependencies and essential services,
  with early attention to potentially costly cloud subscriptions
- Contact employer, insurer, pension and health-benefit administrators and professionals;
  verify survivor eligibility, coverage continuity, account restrictions, and lawful
  access to funds rather than assuming joint accounts remain available

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
- Jurisdiction-specific review of account freezes/access, survivor pensions and health
  coverage, beneficiary savings, controlled-property handling, and provider transfer
  rules; do not apply the reference checklist's European examples as US/Ohio guidance

## Future ideas

- Anonymous group-session facilitator dashboard
- Printable facilitator kit
- Local-only assisted document classification
- Read-only Home Lifecycle Record integration
- Read-only password-manager item-location validation without retrieving secrets
- Native mobile wrappers only if PWA limitations become material
