#!/usr/bin/env py
"""CLI Script for Database Restore Execution (Phase 079)."""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.database.backup_restore import DatabaseBackupManager, RestoreError


def main() -> None:
    """Run database restore CLI tool."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/database_restore.py <path_to_metadata.json>", file=sys.stderr)
        sys.exit(1)

    meta_path = sys.argv[1]
    try:
        manager = DatabaseBackupManager()
        res = manager.restore_backup(metadata_path=meta_path)
        print(f"Restore Successful! File: {res['restored_file']}")
    except RestoreError as exc:
        print(f"Restore Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
