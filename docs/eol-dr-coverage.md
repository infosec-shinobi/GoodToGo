# eol-dr checklist coverage map

Reference: [potatoqualitee/eol-dr — checklist.md](https://github.com/potatoqualitee/eol-dr/blob/main/checklist.md)  
Reviewed for roadmap planning: 2026-11-05  
Source jurisdiction: mixed personal examples, including US and European services  
Content-pack version: not applicable; this is planning research, not shipped guidance

The checklist's strongest contribution is actionable, personal handoff detail: explain
what something is, why it matters, who can help, and what should happen next. GoodToGo
should preserve that plain-language approach without copying example identities,
secrets, spending instructions, or assumptions about legal authority.

## Topic-by-topic disposition

All entries below are **planned**, not newly implemented. Existing broad inventory
categories are not evidence that a complete workflow exists. Milestone references point
to [the roadmap](roadmap.md); MVP 3 captures preparation records, MVP 5 produces offline
handoffs, MVP 6 keeps them current, and MVP 7 guides authorized survivor actions.

| Reference topic | GoodToGo scope and adaptation | Delivery |
| --- | --- | --- |
| Tell family/friends, then announce publicly | Notification order, channel, assigned notifier, and public-announcement preferences; no automated posting or assumed access to private chats | 3.1, 5, 7 |
| Email and forwarding | Primary/recovery/forwarding relationships, operational notices, provider processes, and credential locators | 3.3, 5, 7 |
| Password managers | Emergency-access setup, trusted-person test, and recovery-kit location; never a master-password field or secret-bearing export | 3.3, 5, 6 |
| Phone, MFA, hardware keys, and recovery | Identity recovery chain, device/SIM/VoIP dependencies, authenticator setup/restore-test status, key/spare and recovery-code locations; never PINs, seeds, or codes | 3.3, 5, 6 |
| Keep phones/laptops available | Retention and release prerequisites tied to recovery/preservation needs, not a fixed one-year rule or permission to impersonate the owner | 3.3, 5, 7 |
| Streaming, app-store, family, and other subscriptions | Inventory, payer, billing channel, renewal/notice dates, and keep/cancel/transfer/review preference subject to provider rules | 3.2, 5, 7 |
| Domains, blogs, websites, DNS | Registrar/hosting/DNS relationships, renewals, funding source, intended recipient, and authorized support/transfer process | 3.2–3.3, 5, 7 |
| Cloud subscriptions, sponsorships, and build services | Cost urgency, billing owner, cloud/resource and repository dependencies, technical helper, and intended transfer/shutdown plan | 3.2–3.3, 5, 7 |
| Homelabs and hardware gifts | Recognizable equipment labels, proposed recipients, service dependencies, helper contacts, and preservation/sanitization prerequisites; a wish is not a legal transfer | 3.3, 5, 7 |
| Wireless networks and restart instructions | Device locations, safe restart sequence/waits, outage checks, escalation, and a simpler replacement plan rather than hard-coded vendor timings | 3.3, 5 |
| Home automation / IoT | Essential automations, controller and device inventory, Wi-Fi-change dependencies, and helper-assisted reconnect/simplification plan | 3.3, 5 |
| Social media and public/creative presence | Preserve/export/memorialize/close wishes, business/community dependencies, and official authorized processes; no assumed account sale or unrestricted login | 3.3, 5, 7 |
| Cloud photos and documents | Preserve memories and operational records, choose an export destination, and verify the copy before closing storage | 3.3, 5, 7 |
| Local storage, NAS, and backups | Physical labels/locations, data purpose, safe access locator, restore-test status, and helper-led preservation before disposal | 3.3, 5–7 |
| Wiping drives and Apple activation locks | Device/media-appropriate sanitization and vendor release prerequisites after preservation and authority checks; do not treat a simple format as sufficient | 3.3, 5, 7 |
| Bank accounts, payment wallets, cryptocurrency | Purpose, ownership, custody/recovery-plan location, intended action, and bank/professional contacts; no card PINs, private keys, withdrawal instructions, or promises about access to joint funds | 3.2–3.3, 7–8 |
| Life insurance and investments | Insurer/employer/benefit and investment inventories, claim/provider contacts, beneficiary-review status, and authoritative records; no allocation or investment advice | 3.2, 5, 7 |
| Residual income / automatic deposits | Royalties, creator income, sponsorships, ads and other deposits, receiving account, payer contact, and continuity/closure review | 3.2, 5, 7 |
| Ongoing insurance | Policies, covered people/property, premium source, claim contacts, renewal dates, and coverage-continuity review | 3.2, 5, 7 |
| Credit cards, loans, phone/internet, and auto-pay | Payment dependency map, direct debit versus scheduled bill pay, contract/notice dates, and essential-service review; no advice to pay estate debts personally or use insurance proceeds in a particular way | 3.2, 5, 7 |
| Advisor, accountant, missing income/tax records | Professional contacts and document locations; prior returns/information statements as discovery aids, not automatic extraction or personalized recommendations | 3.1–3.2, 5, 7 |
| Wills, powers of attorney, health directives | Status, authoritative-original location, attorney contact, and authority evidence; not legal-document generation | 3, 5, 7 |
| Retirees and cross-border considerations | Pension survivor contacts, health-coverage continuation, beneficiary savings, and accessible-funds planning questions for banks/professionals; jurisdiction review before guidance | 3.2, 7–8 |
| Security questions and physical security | Record credential/recovery locators and authorized contacts for secured or controlled property; exclude security-question answers, cabinet PINs, and safe combinations | 3.3, 5 |
| Hard copy and refresh schedule | Offline handoff location/current-copy identification, review dates, optional six-month reprint reminder, and trusted-person recovery exercise; external secret kits stay outside GoodToGo | 5–6 |
| Obituary and service | Inclusion/exclusion preferences, photos, music/readings, and burial/cremation wishes distinguished from authoritative documents | 3.1, 5, 7 |
| Pets | Vet, food/medications/routines, identification photos, and agreed caregiver/backups | 3.1, 5, 7 |

## Safety and delivery gates

- Store only credential locators and setup/test status. This exclusion also applies to
  bank/device PINs, security-question answers, authenticator seeds, recovery codes,
  private keys, and physical combinations, including in generated handouts.
- Possession of a device, knowledge of a password, a beneficiary designation, or being
  named as a helper does not establish legal authority or application permissions.
  Use official provider processes, household-scoped authorization, and professional
  review where required.
- Do not turn personal examples into general financial advice, recommend using a
  deceased person's accounts, guarantee recovery from an authenticator backup, or
  prescribe a single sanitization method for all storage. Future actionable guidance
  needs official sources, jurisdiction, review date, and content-pack version.
- Review source attribution/licensing before reusing upstream wording. This document
  maps ideas in original language; it does not import the checklist into the catalog.
- The active MVP remains the private workbook. New question meanings or task rules
  need content versioning and migration review; persistent records need authorization
  tests and schema migrations as applicable. No new architecture is selected here.

## Change impact

Documentation only: no runtime, privacy/storage behavior, schema, workbook content,
backup, or export-format changes. Detailed content design, official-link verification,
professional/jurisdiction review, implementation, and acceptance tests are deferred to
the assigned milestones. Existing release and rollback procedures are unaffected.
