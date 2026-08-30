#!/usr/bin/env python3
"""PostgreSQL WAL Archival & Log Stream Manager for AGENTPAY (P2-01).

Implements PostgreSQL continuous WAL archiving interface (archive_command), WAL segment hashing,
timestamp indexing, and retention management for Point-In-Time Recovery (PITR).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
)
logger = logging.getLogger("agentpay.wal_archiver")


from typing import Any

class WALArchiver:
    """PostgreSQL Write-Ahead Logging (WAL) Continuous Archiver (P2-01)."""

    def __init__(
        self,
        wal_archive_dir: str | Path | None = None,
        retention_hours: int = 72,
    ) -> None:
        self.wal_archive_dir = Path(
            str(wal_archive_dir or os.getenv("WAL_ARCHIVE_DIR", "./wal_archive"))
        ).resolve()
        self.retention_hours = int(os.getenv("WAL_RETENTION_HOURS", str(retention_hours)))
        self.wal_archive_dir.mkdir(parents=True, exist_ok=True)

    def compute_sha256(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a WAL segment."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def archive_segment(self, wal_filepath: str | Path, wal_filename: str) -> dict[str, Any]:
        """Archive a completed PostgreSQL WAL segment file."""
        src_path = Path(wal_filepath)
        dest_path = self.wal_archive_dir / wal_filename

        if not src_path.exists():
            raise FileNotFoundError(f"Source WAL segment path '{src_path}' does not exist.")

        shutil.copy2(src_path, dest_path)
        checksum = self.compute_sha256(dest_path)

        metadata = {
            "wal_filename": wal_filename,
            "archive_path": str(dest_path),
            "size_bytes": dest_path.stat().st_size,
            "checksum_sha256": checksum,
            "archived_at_utc": datetime.now(UTC).isoformat(),
            "status": "ARCHIVED",
        }

        # Save metadata index entry
        meta_file = dest_path.with_suffix(".walmeta.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info("WAL Segment ARCHIVED: name=%s, sha256=%s...", wal_filename, checksum[:12])
        self.purge_expired_wal_segments()
        return metadata

    def purge_expired_wal_segments(self) -> int:
        """Purge WAL segments older than configured retention window."""
        cutoff = datetime.now(UTC) - timedelta(hours=self.retention_hours)
        purged = 0

        for segment in self.wal_archive_dir.glob("*"):
            if segment.suffix in {".walmeta.json", ".tmp"}:
                continue
            try:
                mtime = datetime.fromtimestamp(segment.stat().st_mtime, tz=UTC)
                if mtime < cutoff:
                    meta_file = segment.with_suffix(".walmeta.json")
                    segment.unlink(missing_ok=True)
                    meta_file.unlink(missing_ok=True)
                    purged += 1
                    logger.info("Purged expired WAL segment: %s", segment.name)
            except Exception as exc:
                logger.warning("Error purging WAL segment %s: %s", segment, exc)

        return purged


def main() -> int:
    parser = argparse.ArgumentParser(description="AGENTPAY WAL Archiver")
    parser.add_argument("source", help="Source WAL file path (%p)")
    parser.add_argument("filename", help="WAL filename (%f)")
    parser.add_argument("--archive-dir", help="WAL Archive Directory", default=None)
    args = parser.parse_args()

    archiver = WALArchiver(wal_archive_dir=args.archive_dir)
    try:
        res = archiver.archive_segment(args.source, args.filename)
        print(json.dumps(res, indent=2))
        return 0
    except Exception as err:
        logger.error("WAL Archival failed: %s", err)
        return 1


if __name__ == "__main__":
    sys.exit(main())
