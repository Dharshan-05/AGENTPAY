# AGENTPAY Architecture — Password Hashing (Phase 107)

## Overview
Password hashing in AGENTPAY provides a production-grade, secure, non-deterministic salted password hashing subsystem using Passlib's `CryptContext` with `bcrypt` (and `pbkdf2_sha256` fallback).

## Key Design Principles & Security Controls
1. **Centralized Password Subsystem**: All password hashing and timing-safe verification logic is centralized in `app/core/security.py` (`hash_password`, `verify_password`, `needs_rehash`).
2. **Salt Generation & Non-Deterministic Hashes**: Every call to `hash_password()` generates a unique cryptographic salt, ensuring identical passwords yield distinct hashes.
3. **Timing-Safe Verification**: `verify_password()` performs constant-time password hash comparison, preventing side-channel timing attacks.
4. **Hash Upgrade Evaluation**: `needs_rehash()` evaluates whether a stored credential hash requires rehashing due to scheme deprecation.
5. **Zero Secret Exposure**:
   - Plaintext passwords are NEVER persisted in database tables, logs, audit events, or exceptions.
   - `User` model's `__repr__()` explicitly redacts `password_hash`.
   - API schemas exclude `password_hash` from input and output models.
