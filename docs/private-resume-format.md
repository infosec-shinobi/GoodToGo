# Private resume files: use, format, and offline recovery

Format version: 1  
Last technical review: 2026-11-05 (implementation review, not an independent security audit)

## Use in GoodToGo

1. Complete any part of the private workbook, including safe notes and task edits.
2. Choose a unique, unpredictable resume-file passphrase. Prefer 5–7 randomly chosen
   words; the UI requires at least 16 UTF-16 code units and eight distinct Unicode code
   points, but these checks cannot establish strength. Maximum input length is 1024
   UTF-16 code units. Never reuse an account password.
3. Confirm the passphrase and select **Download encrypted resume file**. Keep the
   passphrase separately from the file. The filename is always
   `goodtogo-private.gtg-resume`, without personal identifiers.
4. Verify that the file saved and test unlocking it before clearing the session.
5. To resume, choose the file, enter its passphrase, and explicitly confirm replacement.
   A successful import replaces rather than merges answers/task edits and switches
   device saving off. Invalid files, wrong passphrases, and incompatible packs do not
   replace the current session. Resume fields clear after an attempted crypto operation.

Lost passphrase means lost access: there is no reset or recovery backdoor. Clearing the
session clears browser fields and aborts pending work, but does not delete files already
downloaded or PDFs already created. Encryption captures a snapshot at download start;
later edits need a new download. Optional device saving remains unencrypted browser
storage and is separate from the encrypted file feature.

Use HTTPS or localhost. A normal HTTP LAN address does not provide Web Crypto's required
secure context. The browser uses about 128 MiB plus overhead for derivation. Offline
fallback may take tens of seconds. Once the page/catalog/scripts have loaded, crypto
and import need no server; reopening a fresh browser page still requires static assets
or a locally retained release. No service worker or offline application cache is added.

## Envelope

A `.gtg-resume` file is UTF-8 JSON, maximum **2,097,152 bytes**:

```json
{
  "format": "goodtogo.private-resume",
  "version": 1,
  "kdf": {
    "name": "scrypt",
    "N": 131072,
    "r": 8,
    "p": 1,
    "salt": "<base64 of 16 random bytes>"
  },
  "cipher": {
    "name": "AES-256-GCM",
    "iv": "<base64 of 12 random bytes>"
  },
  "ciphertext": "<base64 of ciphertext followed by the 16-byte GCM tag>"
}
```

Base64 is canonical RFC 4648 standard alphabet with required padding, no whitespace or
line wrapping. Object key order and JSON whitespace are immaterial. Unknown properties,
versions, algorithms, and KDF parameters are rejected. Required fields must be present.
JSON numbers shown above are fixed values, not negotiable work factors.

Derivation and encryption:

1. Encode the exact passphrase as UTF-8, **without trimming or Unicode normalization**.
2. Derive 32 key bytes using scrypt (RFC 7914), N=2^17, r=8, p=1, the decoded salt.
3. Encrypt the UTF-8 payload with AES-256-GCM, decoded IV, 128-bit authentication tag,
   and additional authenticated data equal to the exact UTF-8/ASCII bytes
   `goodtogo.private-resume/v1` (no newline or terminator).
4. Concatenate ciphertext then tag before base64 encoding. No compression or BOM.

Generate fresh salt and IV using a cryptographic RNG for every export. The reader
checks parameters before allocating KDF memory. The fixed AAD binds the format/version;
all algorithm parameters are fixed and validated. Salt/IV changes invalidate successful
authentication of the payload. There is no plaintext fallback or separate MAC.

## Encrypted payload

Plaintext is UTF-8 JSON, maximum **1,048,576 bytes**, with this schema:

```json
{
  "schema": 1,
  "pack": {"id": "<workbook pack ID>", "version": "<exact workbook version>"},
  "createdAt": "2026-11-05T12:00:00.000Z",
  "state": {
    "<question ID>": "not_sure",
    "<question ID>__note": "Location or safe next step",
    "__tasks": {
      "<question ID with a task>": {
        "included": true,
        "priority": "high",
        "responsiblePerson": "Morgan",
        "targetDate": "2026-12-01"
      }
    }
  }
}
```

`createdAt` is a parseable timestamp of at most 40 characters; writers use ISO 8601 UTC.
The pack ID/version must match the loaded catalog exactly. Unknown payload properties
or state/question/task keys are rejected, with no silent migration or dropping of data.
State may be empty; `__tasks` and individual task fields are optional. Restored missing
fields use the normal workbook/task defaults. Only currently applicable responses/notes
are exported; existing task customizations may remain for temporarily inactive questions.

- Readiness values: `complete`, `in_progress`, `not_started`, `not_sure`,
  `professional_help`, `not_applicable`.
- Applicability values: `yes`, `no`, `not_sure`.
- Safe notes: strings, maximum 4000 UTF-16 code units.
- Task `included`: boolean. `priority`: `critical`, `high`, `medium`, or `low`.
- `responsiblePerson`: string, maximum 120 UTF-16 code units.
- `targetDate`: empty string or a real calendar date in `YYYY-MM-DD` form.

Authenticate, parse, and validate the whole payload before applying it. Render text as
text, not HTML. Notes are organizer information, never passwords, PINs, MFA seeds,
recovery codes, private keys, security answers, or combinations. Encryption does not
turn GoodToGo into a credential vault.

## Independent offline recovery

Keep this specification and `tools/recover_resume.py` with a retained release. On a
trusted computer with Python 3.12+ and the `cryptography` dependency already installed:

```bash
# Install in advance while dependencies are available:
pip install cryptography
# Or, from this repository: pip install -e '.[recovery]'

python tools/recover_resume.py goodtogo-private.gtg-resume recovered-private.json
```

The tool asks for the passphrase through a hidden terminal prompt, not a command-line
argument. It works without the application, server, database, catalog, or network. It
uses the file's authenticated pack metadata rather than needing a matching catalog.
Its output is **unencrypted JSON**: choose a protected destination, inspect it locally,
and remove it when no longer needed. It refuses to overwrite an existing output file.
It does not print answer values, filenames, passphrases, or exception details to logs.
Python and JavaScript cannot guarantee secure erasure of all memory copies.

This envelope is independently implementable with standard libraries, not an existing
ZIP or password-manager file format. Interoperability tests exercise both a Python
writer/browser reader and a browser writer/Python reader. Preserve a matching GoodToGo
release for direct workbook restoration; an older or newer pack is intentionally refused.

## Technical sources

Implementation references reviewed 2026-11-05; these are global technical specifications,
not jurisdiction-specific planning guidance or workbook content-pack changes:

- [RFC 7914: scrypt](https://www.rfc-editor.org/rfc/rfc7914)
- [RFC 4648: base encodings](https://www.rfc-editor.org/rfc/rfc4648)
- [Web Cryptography API](https://www.w3.org/TR/WebCryptoAPI/)
- [OWASP Password Storage Cheat Sheet: scrypt parameters](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#scrypt)
- [scrypt-js upstream](https://github.com/ricmoo/scrypt-js) and local provenance in
  `app/static/vendor/README.md`
