#!/usr/bin/env py
"""CLI Script for Database Backup Execution (Phase 079)."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.database.backup_restore import BackupError, DatabaseBackupManager


def main() -> None:
    """Run database backup CLI tool."""
    try:
        manager = DatabaseBackupManager()
        meta = manager.create_backup()
        print(f"Backup Successful! ID: {meta['backup_id']} File: {meta['filepath']}")
    except BackupError as exc:
        print(f"Backup Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
