# SEC-ADR-004: Agent Identity Governance & Sub-10ms Purge

## Context & Problem Statement
Compromised or rogue agents must be instantly isolated without affecting other tenant services.

## Threat Analysis
Delayed revocation of a compromised agent allows ongoing fraudulent transactions during the response window.

## Decision
Assign immutable GUID identities (`agent_id`) to every agent. Enforce sub-10ms revocation purging via Redis edge cache invalidation.

## Consequences & Trade-Offs
* **Benefits**: Instant global containment of compromised agents.
* **Trade-Offs**: Requires synchronous Redis key eviction on agent status change.
