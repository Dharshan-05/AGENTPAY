# SEC-ADR-006: Cryptographic Payment Authorization Context

## Context & Problem Statement
Payment Orchestration must verify that an incoming payment request was authorized by AGENTGUARD and has not been tampered with.

## Threat Analysis
Adversaries could forge payment execution payloads or bypass AGENTGUARD policy checks to settle funds directly.

## Decision
Require every payment execution request to include a cryptographically signed `Payment Authorization Context` token with a 15-minute expiration TTL.

## Consequences & Trade-Offs
* **Benefits**: Decouples policy authorization from settlement execution; prevents direct execution bypass.
* **Trade-Offs**: Requires authorization token generation and verification step.
