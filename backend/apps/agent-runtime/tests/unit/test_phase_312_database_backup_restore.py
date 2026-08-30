import json
import tempfile
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts.backup_database import DatabaseBackupManager
from scripts.restore_database import DatabaseRestoreManager
from scripts.verify_backup import verify_backup_file
from scripts.wal_archiver import WALArchiver


@pytest.fixture
def temp_dirs() -> Generator[tuple[Path, Path], None, None]:
    with tempfile.TemporaryDirectory() as backup_dir, tempfile.TemporaryDirectory() as wal_dir:
        yield Path(backup_dir), Path(wal_dir)


def test_01_backup_manager_initialization(temp_dirs: tuple[Path, Path]) -> None:
    """Test 1: DatabaseBackupManager initializes correctly with custom retention."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir, retention_days=14)
    assert mgr.retention_days == 14
    assert mgr.backup_dir == b_dir.resolve()


def test_02_backup_filename_format(temp_dirs: tuple[Path, Path]) -> None:
    """Test 2: Backup filename generation produces timestamped sql.gz names."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    fname = mgr.generate_backup_filename()
    assert fname.startswith("agentpay_db_dump_")
    assert fname.endswith(".sql.gz")


def test_03_full_backup_creation_and_checksum(temp_dirs: tuple[Path, Path]) -> None:
    """Test 3: create_full_backup produces backup file, metadata manifest, and valid SHA-256 hash."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()

    assert res["status"] == "SUCCESS"
    assert "checksum_sha256" in res
    assert Path(str(res["backup_path"])).exists()

    meta_file = Path(str(res["backup_path"])).with_suffix(".json")
    assert meta_file.exists()


def test_04_backup_verification_script_validates_artifact(temp_dirs: tuple[Path, Path]) -> None:
    """Test 4: verify_backup_file confirms SHA-256 hash match and gzip integrity."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()
    b_path = Path(str(res["backup_path"]))

    verification = verify_backup_file(b_path)
    assert verification["status"] == "VALID"
    assert verification["hash_verified"] is True
    assert verification["gzip_verified"] is True


def test_05_verify_backup_detects_corrupted_artifact(temp_dirs: tuple[Path, Path]) -> None:
    """Test 5: verify_backup_file detects corrupted file stream."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()
    b_path = Path(str(res["backup_path"]))

    # Corrupt the backup file
    with open(b_path, "wb") as f:
        f.write(b"CORRUPTED_NON_GZIP_DATA")

    with pytest.raises((RuntimeError, OSError, ValueError)):
        verify_backup_file(b_path)


def test_06_verify_backup_detects_tampered_checksum(temp_dirs: tuple[Path, Path]) -> None:
    """Test 6: verify_backup_file detects tampered manifest SHA-256 mismatch."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()
    b_path = Path(str(res["backup_path"]))
    meta_path = b_path.with_suffix(".json")

    # Tamper with manifest
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    meta["checksum_sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

    verification = verify_backup_file(b_path)
    assert verification["status"] == "INVALID"
    assert verification["hash_verified"] is False


def test_07_wal_archiver_segment_copy_and_manifest(temp_dirs: tuple[Path, Path]) -> None:
    """Test 7: WALArchiver archives segment file and generates metadata."""
    _, wal_dir = temp_dirs
    archiver = WALArchiver(wal_archive_dir=wal_dir)

    # Create dummy WAL segment file
    dummy_src = wal_dir / "000000010000000000000001.tmp"
    with open(dummy_src, "wb") as f:
        f.write(b"DUMMY_POSTGRES_WAL_LOG_SEGMENT_DATA")

    res = archiver.archive_segment(dummy_src, "000000010000000000000001")
    assert res["status"] == "ARCHIVED"
    assert (wal_dir / "000000010000000000000001").exists()
    assert (wal_dir / "000000010000000000000001.walmeta.json").exists()


def test_08_wal_archiver_missing_source_raises_file_not_found(temp_dirs: tuple[Path, Path]) -> None:
    """Test 8: Archiving missing WAL segment raises FileNotFoundError."""
    _, wal_dir = temp_dirs
    archiver = WALArchiver(wal_archive_dir=wal_dir)
    with pytest.raises(FileNotFoundError):
        archiver.archive_segment(wal_dir / "non_existent.wal", "non_existent.wal")


def test_09_database_restore_manager_verification(temp_dirs: tuple[Path, Path]) -> None:
    """Test 9: DatabaseRestoreManager verifies backup before restore."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()
    b_path = Path(str(res["backup_path"]))

    restore_mgr = DatabaseRestoreManager()
    assert restore_mgr.verify_backup_integrity(b_path) is True


def test_10_database_restore_execution_workflow(temp_dirs: tuple[Path, Path]) -> None:
    """Test 10: DatabaseRestoreManager executes restore workflow and returns success metadata."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()
    b_path = Path(str(res["backup_path"]))

    restore_mgr = DatabaseRestoreManager()
    restore_res = restore_mgr.execute_restore(b_path)
    assert restore_res["status"] == "RESTORE_SUCCESSFUL"
    assert restore_res["integrity_verified"] is True


def test_11_pitr_timestamp_recovery_validation(temp_dirs: tuple[Path, Path]) -> None:
    """Test 11: Execute restore with explicit target PITR recovery timestamp."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()
    b_path = Path(str(res["backup_path"]))

    restore_mgr = DatabaseRestoreManager()
    target_dt = datetime.now(UTC)
    restore_res = restore_mgr.execute_restore(b_path, target_timestamp=target_dt)

    assert restore_res["status"] == "RESTORE_SUCCESSFUL"
    assert restore_res["target_timestamp"] == target_dt.isoformat()


def test_12_secret_redaction_in_backup_metadata(temp_dirs: tuple[Path, Path]) -> None:
    """Test 12: Backup metadata manifests exclude database password and secrets."""
    b_dir, _ = temp_dirs
    mgr = DatabaseBackupManager(backup_dir=b_dir)
    res = mgr.create_full_backup()

    dumped_str = json.dumps(res)
    assert "postgres_password" not in dumped_str
    assert "key_secret" not in dumped_str
    assert "webhook_secret" not in dumped_str
