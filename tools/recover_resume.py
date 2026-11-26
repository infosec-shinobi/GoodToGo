"""Recover a v1 resume file offline; no application, database, or server required."""

import argparse
import base64
import getpass
import hashlib
import json
import sys
from pathlib import Path

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_PLAIN_BYTES = 1024 * 1024
AAD = b"goodtogo.private-resume/v1"


def decode(value: str, length: int | None = None) -> bytes:
    data = base64.b64decode(value, validate=True)
    if base64.b64encode(data).decode("ascii") != value or (length and len(data) != length):
        raise ValueError("Invalid encoding")
    return data


def decrypt_resume(contents: bytes, password: str) -> dict:
    # Optional dependency: pip install '.[recovery]' (or cryptography standalone).
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    if len(contents) > MAX_FILE_BYTES or not 1 <= len(password) <= 1024:
        raise ValueError("Invalid input size")
    envelope = json.loads(contents)
    if set(envelope) != {"format", "version", "kdf", "cipher", "ciphertext"}:
        raise ValueError("Unsupported envelope")
    kdf, cipher = envelope["kdf"], envelope["cipher"]
    if (
        envelope["format"] != "goodtogo.private-resume"
        or type(envelope["version"]) is not int
        or envelope["version"] != 1
        or set(kdf) != {"name", "N", "r", "p", "salt"}
        or kdf["name"] != "scrypt"
        or any(type(kdf[key]) is not int for key in ("N", "r", "p"))
        or (kdf["N"], kdf["r"], kdf["p"]) != (131072, 8, 1)
        or set(cipher) != {"name", "iv"}
        or cipher["name"] != "AES-256-GCM"
    ):
        raise ValueError("Unsupported parameters")
    salt = decode(kdf["salt"], 16)
    iv = decode(cipher["iv"], 12)
    ciphertext = decode(envelope["ciphertext"])
    if not 16 <= len(ciphertext) <= MAX_PLAIN_BYTES + 16:
        raise ValueError("Invalid ciphertext size")
    key = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=131072, r=8, p=1,
        dklen=32, maxmem=256 * 1024 * 1024,
    )
    payload = json.loads(AESGCM(key).decrypt(iv, ciphertext, AAD))
    if (
        set(payload) != {"schema", "pack", "createdAt", "state"}
        or payload["schema"] != 1
        or not isinstance(payload["state"], dict)
    ):
        raise ValueError("Unsupported payload")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resume", type=Path)
    parser.add_argument(
        "output", type=Path, help="New plaintext JSON file; protect and remove it safely"
    )
    args = parser.parse_args()
    print("Warning: recovery creates sensitive, unencrypted JSON. Keep it secure.", file=sys.stderr)
    try:
        with args.resume.open("rb") as source:
            contents = source.read(MAX_FILE_BYTES + 1)
        payload = decrypt_resume(contents, getpass.getpass("Resume-file passphrase: "))
        # Exclusive creation: never overwrite existing files.
        with args.output.open("x", encoding="utf-8") as output:
            json.dump(payload, output, ensure_ascii=False, indent=2)
            output.write("\n")
    except (Exception, KeyboardInterrupt):
        print(
            "Recovery failed. Check the file, passphrase, dependencies, and output path.",
            file=sys.stderr,
        )
        return 1
    print(
        "Recovered to the requested plaintext file. Protect it as private information.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
