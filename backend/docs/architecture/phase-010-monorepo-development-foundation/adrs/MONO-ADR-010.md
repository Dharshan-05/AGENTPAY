# MONO-ADR-010: Zero Committed Plaintext Secrets Policy

## Context & Problem Statement
Preventing secret leakage (Razorpay keys, JWT secrets, database passwords) into Git repositories.

## Decision
Ban plaintext production credentials in Git. Enforce automated pre-commit secret scanning using Gitleaks.

## Consequences & Trade-Offs
* **Benefits**: 100% protection against accidental public repository secret leaks.
* **Trade-Offs**: Requires developers to configure Gitleaks locally or run pre-commit hooks.
