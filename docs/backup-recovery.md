# Backup and Recovery Strategy

Status: Target design for persistent MVPs

## Recovery objectives

Two different recovery paths are required:

1. **Application recovery:** Restore the running service after infrastructure or data
   loss.
2. **Family recovery:** Access useful information without restoring the application.

The offline survival package addresses family recovery. Backups address application
recovery. Neither replaces the other.

## Backup set

- PostgreSQL logical or physical backup
- Encrypted document objects
- Content-pack versions used by stored records
- Application release identifier
- Encryption metadata
- Separately protected key-encryption material
- Configuration template without runtime secrets
- Restore instructions

## Proposed schedule

- PostgreSQL backup nightly
- Document-storage snapshot nightly after database backup
- Encrypted offsite copy daily or at least weekly
- Retain daily copies for 14 days
- Retain weekly copies for 8 weeks
- Retain monthly copies for 12 months
- Review retention after actual storage measurements

## Key separation

Backups of ciphertext are useless after losing required decryption keys. Storing the only
key beside the only backup also defeats much of the protection.

- Protect key material separately from database and document backups.
- Keep at least two recovery-key copies in different failure domains.
- Document who can retrieve them.
- Test key rotation against restored historical backups.
- Never commit keys to Git or place them in the exported repository.

## Restore drill

At least quarterly in production:

1. Provision an isolated temporary environment.
2. Restore the database.
3. Restore document objects.
4. Restore the correct key material.
5. Start the matching application version.
6. Verify household counts and referential integrity.
7. Decrypt a controlled test record and test document.
8. Generate and open an authorized export.
9. Record duration, failures, and corrective tasks.
10. Securely destroy the temporary environment.

## Survival-package cadence

- Generate after major changes.
- Remind at least annually.
- Display age prominently.
- Keep the full package encrypted.
- Store the recovery key separately.
- Have a trusted person locate and open a test package annually.

## Failure cases to test

- Application host destroyed
- Database available but documents missing
- Documents available but database missing
- Current key lost
- Historical key needed after rotation
- Backup corrupted
- Backup credentials unavailable because the administrator is incapacitated
- DNS and reverse proxy unavailable
- Household member has the export but not the recovery key

