# MVP 1.4: GoodToGo branding integration

Date: 2026-11-07  
Status: Implemented; automated validation complete; manual release checks remain.

## User-visible result

The running site now uses the supplied GoodToGo identity instead of the “FR” prototype
mark: one compact header logo, primary tagline, category/readiness icons, favicons, local
Manrope headings and Inter body/forms, and brand-aligned light/dark surfaces. Default
ocean colors follow the brand; the other four accent choices remain available. Existing
theme settings and system-mode changes still work. Labels, not icons alone, identify
navigation and categories. The clipboard is only the readiness/navigation icon.

Printed workbooks and take-home lists use a small unchanged monochrome symbol plus
the name/tagline. Handwriting space, full notes, source/pack/review metadata, and
privacy/safety notices remain. No question meaning or task rules have changed.

After user visual feedback, the duplicate hero logo was removed, the header artwork
was reduced to 112–130px wide (preserving aspect ratio), and topic cards use a fluid
three/two/one-column grid with one square, consistently aligned icon per category.
The legal/health category uses one legal icon rather than a mismatched pair. Type and
gutters scale fluidly, with geometry tests at 320–1920px, including intermediate widths.

## Asset mapping and update policy

All artwork below is copied unchanged from `docs/branding/` into the corresponding
`app/static/branding/` subdirectory. The documentation tree itself is not public.

| Master path under `docs/branding/` | Runtime use |
| --- | --- |
| `logos/svg/goodtogo-horizontal.svg` | Compact header logo on white in light mode |
| `logos/svg/goodtogo-horizontal-dark.svg` | Transparent dark-mode header adaptation with Pale Blue lettering |
| `logos/svg/goodtogo-symbol-monochrome.svg` | Small print identity on every printable view |
| `icons/svg/life-plan.svg` | Private workbook navigation |
| `icons/svg/family.svg` | People and responsibilities |
| `icons/svg/legal.svg` | Legal and health readiness |
| `icons/svg/financial.svg` | Financial and insurance inventory |
| `icons/svg/digital.svg` | Digital life |
| `icons/svg/documents.svg` | Household continuity |
| `icons/svg/legacy.svg` | Wishes, communication, and handoff |
| `favicons/goodtogo-favicon.svg`, `favicon-32.png`, `favicon.ico` | Browser favicon variants |
| `favicons/favicon-180.png` | Apple touch icon |
| `web/brand-tokens.css` | Unchanged base brand tokens loaded before semantic app CSS |

The new compact dark master was adapted from `goodtogo-horizontal.svg` after user
feedback about the bright white dark-mode logo panel. Geometry, typography, and size
are unchanged; the wordmark and road highlight use the existing Pale Blue brand color,
not pure white. No background rectangle or image filter is used. The original light
and print masters remain unchanged. CSS selects one header image according to the
cached theme and system preference, including live OS theme changes.

Runtime folders omit the master's intermediate `svg/` or `web/` directory. Only
selected public assets are copied. Update the masters and runtime copies together;
tests compare bytes and reject scripted or externally dependent SVG content. Artwork
keeps intrinsic aspect ratio, original typography/colors, and no filters or shadows.
White icon plaques preserve navy artwork legibility across all accent schemes.

Fonts were obtained from the Google Fonts **source repository at development time**,
not through a browser font service. Unmodified variable TrueType files, SIL OFL 1.1
notices, immutable upstream blob IDs, and SHA-256 hashes are recorded in
`app/static/fonts/README.md`. They add about 1 MiB before compression, with
`font-display: swap` and system fallbacks. WOFF2/subsetting is deferred optimization.
The supplied brand packet remains unchanged and does not gain downloaded font files.

## Contrast and theme decisions

- Light backgrounds use Off White `#F8FAFC`, White, Ink `#1D2935`, Slate `#566574`,
  Deep Navy `#102D4F`, and Pale Blue `#DCEAF7` from the packet.
- Clear Blue `#4C8FD6` has only **3.38:1** contrast against white: it remains in
  artwork, the ocean progress bar, and decorative accents, not white-text buttons.
  The light action/link variant `#2565A0` provides **6.09:1** against white and
  **4.98:1** against Pale Blue.
- Dark ocean uses the original navy on surfaces with a darker background, pale text,
  and a lighter action/link variant `#72B1EE`. Dark buttons and task-number badges
  use dark foreground text instead of low-contrast white.
- Forest light accent is adjusted to `#147A3A` and plum dark to `#C58AFA` to maintain
  text contrast on the new shared surfaces. Their identities/preferences are preserved;
  the logo never adopts a user's accent color.
- Control boundaries/focus indicators are explicit; danger/critical text has a light
  dark-mode variant. Excluded tasks use a dashed border rather than fading text.
  Colored callout labels use the panel's contrast-safe foreground.
- The small header logo uses white only in light mode. Dark mode has a transparent
  backing and softer Pale Blue lettering; explicit and system themes select the correct
  artwork with CSS. Early cached theme attributes and render-blocking CSS retain
  correct initial styling. Reduced motion disables smooth scrolling and progress animation.
- Public stylesheet URLs include a content-derived version, with strict browser-test
  validation of those hashes. Small HTML image dimensions prevent large source SVG
  sizes from taking over the layout if CSS is missing or a previous stylesheet is cached.
- Print disables contextual ligatures/alternates so the font's special punctuation
  glyphs do not replace ordinary date separators in searchable/extracted PDF text.

## Security, privacy, and migration impact

Only same-origin public fonts/images/CSS are added. No CDN, remote font import,
analytics, third-party scripts, answer endpoints, new storage, or altered CSP is needed.
Private-session network tests explicitly enumerate new asset paths; they are not
weakened to permit arbitrary static/external traffic. SVGs retain no external resources.
Fonts and artwork are included in the wheel and Docker application copy, not fetched
from upstream at application startup.

No database, content-pack, browser preference/storage, or resume-format migration.
Existing encrypted resume files remain compatible. Server backup policy is unchanged;
print/PDF outputs retain their content and are usable without the running app. Font
files and images become part of the versioned application release, not household data.

## Validation

- `pytest`: **32 passed**, including browser privacy/resume/print regressions, local
  asset/source parity, font hashes/licenses, and all existing catalog/domain tests.
- `ruff check .` and `git diff --check`: passed.
- New browser matrix covers 390px/1440px widths, all five accent schemes, explicit
  light/dark, and system mode under light/dark OS settings: 40 combinations. It checks
  local asset loads, cached theme initialization, compact undistorted logo/icon sizes,
  no duplicate hero artwork or horizontal overflow,
  font availability, and computed text/control contrast. Axe WCAG 2 A/AA and 2.1 AA
  scans cover home plus private/settings pages in explicit modes, and home in system
  modes. Additional geometry tests exercise seven widths from 320px to 1920px, verify
  one/two/three card columns, and assert fluid heading sizes. Separate tests cover
  setting changes, system changes, reduced motion, keyboard focus, and blank handouts.
- Privacy tests still observe only enumerated same-origin GET requests during answer
  editing, saving, encrypted export/import, printing, and clearing; private canaries
  stay out of URLs, bodies, headers, and console output.
- Wheel build and archive inspection verify all selected brand/font files and the shared
  template are packaged, with no documentation tree. Docker image build and packaged
  route/asset smoke checks pass; development-only `node_modules` is excluded from context.
- Initial light/dark and print-emulation screenshots, followed by revised light
  desktop/tablet/mobile screenshots after user feedback, were visually inspected.
  Browser PDF text tests verify full notes, dates, metadata, and
  source appendices; the print identity is visible without background printing.

These checks do not claim full accessibility conformance or physical-device testing.

## Release and rollback

Deploy the shared templates, CSS, `app/static/branding/`, and `app/static/fonts/`
together. Rebuild the wheel/container; partial CSS/template deployment can cause missing
fonts or artwork. Retain font notices with the packaged files. Normal static cache
refresh uses public stylesheet content-version queries; no service worker, PWA,
or private-data cache infrastructure is introduced.

Rollback by redeploying the previous application revision's templates/static assets
together. Do not clear household data, local answers, preferences, or downloaded resume
files. No database/catalog rollback is required.

## Deferred work

- Real Android/device and manual screen-reader checks, additional browser engines,
  zoom/reflow inspection, and physical Letter black-and-white printer checks.
- User acceptance of the visual treatment; further layout refinements can follow
  without changing workbook meanings or approved artwork.
- Optional WOFF2/font subsetting after license/provenance and coverage review.
- Earlier MVP 1.3 independent crypto and physical-device release gates remain open;
  branding completion does not certify those gates or enable persistent households.
