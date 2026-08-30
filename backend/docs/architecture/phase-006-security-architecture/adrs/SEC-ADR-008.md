# SEC-ADR-008: Production Secrets Management & Zero-Git Policy

## Context & Problem Statement
Hardcoded database credentials or API keys in source control expose the system to catastrophic compromise.

## Threat Analysis
Public or internal repository leaks could expose Razorpay master secrets, allowing attackers to manipulate financial rails.

## Decision
Enforce a Zero-Git secrets policy. Inject production secrets dynamically from Vault/KMS at container startup; scan commits automatically using TruffleHog.

## Consequences & Trade-Offs
* **Benefits**: Eliminates credential exposure in source code repositories.
* **Trade-Offs**: Requires deploying secret manager infrastructure in production environments.
