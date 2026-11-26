# Local brand typography

Downloaded unchanged from the Google Fonts source repository on 2026-11-07. These
are variable TrueType fonts with their full upstream character coverage, not subsets.
They add approximately 1 MiB before HTTP compression and are cached normally by the
browser. WOFF2/subsetting can be evaluated later without adding a font service.

| Local file | Upstream file (google/fonts) | Immutable Git blob | SHA-256 |
| --- | --- | --- | --- |
| `Manrope-variable.ttf` | `ofl/manrope/Manrope[wght].ttf` | `75274da58537d6123b14f2cd0c355ad4681fc2b3` | `3ae11c49db0455a3cc33e37d380f20fdb8c7f8b41dc07625c177e3d87a9d6ae6` |
| `Inter-variable.ttf` | `ofl/inter/Inter[opsz,wght].ttf` | `047c92f6e2212473dc436020afed689527076d44` | `29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031` |

Sources:

- <https://github.com/google/fonts/tree/main/ofl/manrope>
- <https://github.com/google/fonts/tree/main/ofl/inter>
- Immutable files are retrievable with
  `https://api.github.com/repos/google/fonts/git/blobs/<Git blob>`.

Both use the SIL Open Font License 1.1. Preserve the downloaded copyright/license
notices in `Manrope-OFL.txt` and `Inter-OFL.txt`. No font files are modified or renamed
internally. CSS uses normal Manrope weights 200–800 for headings and Inter 100–900 for
body/forms, `font-display: swap`, and the brand packet's system fallbacks. Logo SVGs
retain their original embedded typography; they are not retypeset using these fonts.

All runtime URLs are same-origin. Upstream URLs here are provenance, never browser
imports. Future updates need source/license/hash review and browser/print checks.
