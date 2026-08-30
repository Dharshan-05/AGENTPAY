"""Opaque token generation and cryptographic digest module for AGENTPAY."""

import hashlib
import secrets


def generate_opaque_token(bytes_count: int = 64) -> str:
    """Generate cryptographically secure URL-safe opaque random refresh token string."""
    return secrets.token_urlsafe(bytes_count)


def hash_token(raw_token: str) -> str:
    """Compute one-way SHA-256 cryptographic hex digest of raw token string.

    Never persists or logs plaintext tokens in database records or logs.
    """
    if not raw_token:
        return ""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
