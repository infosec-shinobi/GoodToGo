# MVP 1.3: Private resume and export review

Date: 2026-11-05  
Status: Prototype implemented; automated checks passing; independent/manual release
gates remain open. This does not mark all of MVP 1 complete.

## User-visible result

- Download and unlock encrypted private resume files entirely in the browser. Export
  includes active answers/safe notes and task selection, priorities, people, and dates.
- Passphrase confirmation, length/repetition feedback, random-word advice, and explicit
  loss warnings; passphrases are not saved as preferences or answers.
- Import requires replacement confirmation. Malformed, incompatible, tampered, or
  wrong-passphrase files leave current answers intact. Successful import replaces the
  session and turns device saving off. Clear cancels in-flight operations.
- Separate blank workbook at `/private/workbook/blank`, with all questions including
  conditional paper instructions and a public source appendix; it never reads answers.
- Completed workbook print displays selected answers and complete wrapping notes,
  rather than clipped textarea contents, and repeats a sensitive/version/date footer.
- A note-to-task focus issue found by browser tests is fixed: blurring workbook notes
  no longer regenerates the task controls that the participant is moving into.

## Security and privacy impact

The new [format](private-resume-format.md) uses fixed-cost scrypt and AES-256-GCM with
fresh salt/IV. No server-side answer processing, upload route, telemetry, or remote
runtime dependency is added. The scrypt library and worker are local public assets.
Plaintext processing stays in the browser; encryption needs HTTPS or localhost. There
is no weak-crypto/plaintext fallback. The already-loaded async KDF works offline when
workers cannot load. Best-effort byte clearing is not a browser-memory-erasure guarantee.

Imports enforce size, exact format/algorithm/cost, authentication, exact pack match,
and field validation before applying state. Errors shown to users are fixed messages,
not payloads or library exception details. Local-device answer saving remains opt-in
and unencrypted; it is not made secure merely by adding an encrypted file feature.

The file allows offline passphrase guessing. Passphrase checks do not guarantee entropy.
Independent cryptographic review is still required before production security claims.
This is an organizer, not a credential vault. Print/PDF outputs are unencrypted and
the UI warns about saved-file and printer retention.

## Schema, content, backup, and recovery impact

No database schema migration or workbook pack-version change. Question meanings and
task definitions are unchanged. Safe notes now have a 4000-character input/export
validation limit; existing longer saved notes are not silently truncated. Users must
shorten them before exporting, or preserve them through print.

The browser-storage key and task fields remain compatible. The new versioned resume
envelope is separate from browser local storage. Unsupported pack versions are refused,
not migrated. Server backups are unchanged. Keep the resume passphrase separately from
the file, and retain the format specification and standalone Python recovery tool.
Offline recovery needs Python plus its preinstalled crypto dependency, not the running
application. Recovery writes sensitive plaintext only to an explicitly named new file.

## Tests run

- `pytest`: **23 passed**, including all six real-browser cases; one existing upstream
  Starlette/httpx deprecation warning.
- `ruff check .`: passed.
- `git diff --check`: passed (Git reports normal working-copy CRLF notices).
- Dependency-free Node tests run through pytest: upstream SHA-256, RFC 7914 vector,
  random salt/IV, Unicode roundtrip, native Node scrypt interoperability, wrong password,
  tamper, incompatible pack, malformed state/cost/size/version, and existing task logic.
- Real Chromium tests at 390px/1440px observe requests during answer/note/task edits,
  save/reload, encrypted download, invalid/successful import, print, and clear. Canary
  private values do not appear in request URLs/bodies/headers or console output; only
  expected public GET requests occur, with no WebSockets or page errors.
- Browser-exported files recover through Python's independent implementation;
  Python-created files import in the browser. Authenticated invalid state and pack
  mismatch do not overwrite the session. Clearing during KDF work does not restore it.
- Browser offline import, secure-context failure, PDF text extraction, blank-sheet
  isolation, keyboard focus order, and pinned local axe WCAG 2 A/AA/2.1 AA scans pass.
  Axe scans cover the private workbook with a generated task and both blank handouts.

## Deferred release checks

- Independent cryptographic/dependency review and broader malformed-file fuzzing.
- Real Android/low-memory device performance; viewport tests are not device testing.
- Manual screen-reader, physical Letter print, and visual page-break inspection across
  browsers, long notes, all color schemes, and black-and-white printers. Automated
  Chromium PDF text checks and axe scans do not prove complete accessibility or print
  quality. Non-Chromium browser coverage remains open.
- Content-pack migration/import preview and durable household import belong to later
  work. No automatic merge, secret vaulting, or server-side PDF renderer is added.

## Release and rollback

Deploy routes, templates, all static scripts (including vendor/worker files), and CSS
together behind HTTPS, or use localhost for development. Do not enable persistent
household data as part of this milestone. Keep dependencies available for offline
recovery before relying on encrypted files. Test download/unlock before clearing data.

For rollback, redeploy the previous application revision; no database/catalog rollback
is needed. Prior versions ignore resume files but continue reading the existing local
answer-storage format. Preserve this release, the format specification, the file's
matching content pack, and the offline recovery tool for files already exported. Do not
delete users' downloaded files or browser storage as part of rollback.
