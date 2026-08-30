# SEC-ADR-002: User MFA & Cryptographic HMAC Agent Authentication

## Context & Problem Statement
The platform serves two distinct principal classes: human owners and autonomous AI agents. A unified authentication mechanism cannot satisfy both requirements.

## Threat Analysis
Stolen session tokens or plain API key forgery would allow attackers to impersonate users or agents to drain financial balances.

## Decision
Enforce Argon2id hashed passwords with TOTP MFA for human users. Enforce HMAC-SHA256 request header signatures (`X-Agent-Signature`) with 15-minute Redis nonce caching for AI agents.

## Consequences & Trade-Offs
* **Benefits**: Cryptographic proof of origin for agent intents; eliminates replay attacks.
* **Trade-Offs**: Requires agents to sign payloads using an assigned secret key.
