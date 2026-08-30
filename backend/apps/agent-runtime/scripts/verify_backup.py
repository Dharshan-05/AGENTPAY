#!/usr/bin/env python3
"""Backup Verification & SHA-256 Integrity Inspector for AGENTPAY (P2-01).

Validates backup archive structures, checksum matches, and manifest details.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
)
logger = logging.getLogger("agentpay.verify_backup")


from typing import Any

def verify_backup_file(backup_path: Path) -> dict[str, Any]:
    """Verify backup file readability, gzip stream, and SHA-256 hash match."""
    backup_path = backup_path.resolve()
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file '{backup_path}' does not exist.")

    # Calculate SHA-256
    sha256 = hashlib.sha256()
    with open(backup_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    actual_hash = sha256.hexdigest()

    # Read manifest if present
    meta_path = backup_path.with_suffix(".json")
    expected_hash = None
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            expected_hash = meta.get("checksum_sha256")

    # Read gzip content test
    is_valid_gzip = False
    uncompressed_bytes = 0
    with gzip.open(backup_path, "rb") as gz:
        while chunk := gz.read(65536):
            uncompressed_bytes += len(chunk)
        is_valid_gzip = True

    hash_match = True if expected_hash is None else (actual_hash == expected_hash)

    result = {
        "backup_file": backup_path.name,
        "size_bytes": backup_path.stat().st_size,
        "uncompressed_bytes": uncompressed_bytes,
        "sha256_hash": actual_hash,
        "expected_hash": expected_hash,
        "hash_verified": hash_match,
        "gzip_verified": is_valid_gzip,
        "status": "VALID" if (hash_match and is_valid_gzip) else "INVALID",
    }

    logger.info("Backup Verification Result for %s: %s", backup_path.name, result["status"])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="AGENTPAY Backup Verification Tool")
    parser.add_argument("backup_file", help="Path to backup file")
    args = parser.parse_args()

    try:
        res = verify_backup_file(Path(args.backup_file))
        print(json.dumps(res, indent=2))
        return 0 if res["status"] == "VALID" else 1
    except Exception as err:
        logger.error("Verification failed: %s", err)
        return 1


if __name__ == "__main__":
    sys.exit(main())
