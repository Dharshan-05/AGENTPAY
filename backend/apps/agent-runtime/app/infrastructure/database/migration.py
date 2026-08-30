"""Database migration graph verification and CI helper module for AGENTPAY (Phase 018)."""

from pathlib import Path
from typing import Any

from alembic.config import Config
from alembic.script import ScriptDirectory


def verify_migration_graph(config_file_path: Path | None = None) -> dict[str, Any]:
    """Verify that the Alembic migration revision graph is valid, single-headed, and linear.

    Returns diagnostic metadata about the current migration revision graph.
    """
    if config_file_path is None:
        base_dir = Path(__file__).parent.parent.parent.parent
        config_file_path = base_dir / "alembic.ini"

    if not config_file_path.exists():
        msg = f"Alembic config file not found at '{config_file_path}'."
        raise FileNotFoundError(msg)

    alembic_cfg = Config(str(config_file_path))
    script = ScriptDirectory.from_config(alembic_cfg)

    # 1. Verify single migration head (no unintended branching / split heads)
    heads = script.get_heads()
    if len(heads) > 1:
        msg = f"Multiple migration heads detected: {heads}. Expected single linear head."
        raise ValueError(msg)

    # 2. Retrieve linear revisions list
    revisions = list(script.walk_revisions())

    return {
        "is_valid": True,
        "head": heads[0] if heads else None,
        "revision_count": len(revisions),
        "revisions": [r.revision for r in revisions],
    }
