#!/usr/bin/env py
"""CLI Script for Database Backup Verification (Phase 079)."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.database.backup_restore import BackupError, DatabaseBackupManager


def main() -> None:
    """Run database backup verification CLI tool."""
    if len(sys.argv) < 2:
        print(
            "Usage: python scripts/database_backup_verify.py <path_to_metadata.json>",
            file=sys.stderr,
        )
        sys.exit(1)

    meta_path = sys.argv[1]
    try:
        manager = DatabaseBackupManager()
        res = manager.verify_backup(metadata_path=meta_path)
        print(f"Backup Verification PASSED! SHA-256 Checksum: {res['checksum']}")
    except BackupError as exc:
        print(f"Verification Failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
