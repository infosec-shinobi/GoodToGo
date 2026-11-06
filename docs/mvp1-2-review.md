# MVP 1.2: Take-home list review

Date: 2026-10-25
Status: Implemented and automated tests passing; manual release checks pending.

## User-visible result

- Selected tasks retain optional responsible-person and target-date fields through
  answer changes and priority adjustments, and through reload when saving is enabled.
- Take-home printing omits excluded tasks, shows assignments as wrapping text, and
  supplies a completion checkbox and space for handwritten notes.
- A source appendix follows the selected tasks, deduplicates their sources, and shows
  jurisdiction, link-verification dates, pack version, and last-reviewed date. Metadata
  is from the catalog; this release does not perform live link verification.
- Paper participants can use `/private/take-home/blank`, with six empty task spaces
  and the full public source appendix. No private-session data is read by this page.

## Security, privacy, and migration impact

No answer endpoint, telemetry, new external assets, or database writes were added.
Assignments use the existing opt-in local answer storage (`__tasks`); the storage key
and existing selection/priority fields remain compatible. Manual and inactivity clear
now both discard all task customizations, including assignments. Assigning a person
does not grant permissions or legal authority. User text is rendered with `textContent`
or input values, not HTML. Printouts/PDFs are sensitive and the UI warns about retention.

No database migration, content-pack change, or architectural decision is required.
Workbook wording and task definitions are unchanged. No server backup changes are
needed; printed/PDF materials remain usable without the running application.

## Automated validation

- `pytest`: 16 passed (one upstream Starlette/httpx deprecation warning).
- `ruff check .`: passed.
- Pytest runs `node --test tests/js/workbook.test.cjs` when Node.js is available.
  These dependency-free DOM-fixture tests execute the actual workbook script and cover
  local-only assignments, typing without replacing focused controls, regeneration,
  opt-in saving/reload, saving-off removal, priority/selection preservation, selected
  source metadata, and manual/inactivity clearing.
- Route tests check the standalone blank handout, public source metadata, print hooks,
  and privacy notices. Existing catalog-only network and no-submission checks pass.

DOM-fixture tests are not real-browser network or layout tests. Labels wrap their
inputs, input/select focus indicators use theme tokens, and print priority includes
text rather than relying on color. These implementation checks do not establish
full accessibility conformance.

## Deferred release checks and work

- Real-browser keyboard/screen-reader and automated accessibility checks.
- Android/desktop layout and physical Letter black-and-white print inspection,
  including long names, many selected tasks, dark themes, notes, and appendix paging.
- Real-browser no-answer-network verification and encrypted resume files (MVP 1.3).
- Live source-link re-verification, professional content review, durable household
  assignment, reminders, and server-rendered PDFs remain outside this slice.

## Release and rollback

Deploy the application templates, static files, and new public route together. No
database or catalog migration is needed. Existing saved sessions need no conversion.
For rollback, redeploy the prior application revision; unknown assignment keys in
`__tasks` do not affect the previous selection/priority reader. Users should print
needed assignments before rollback because the older UI cannot display or edit them.
Use Clear this session to remove browser-local private information on shared devices.
