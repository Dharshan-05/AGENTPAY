# API-ADR-010: Redis Sliding-Window Multi-Tier Rate Limiting Engine

## Context & Problem Statement
Protecting API endpoints against denial-of-service (DoS) floods and API token abuse.

## Decision
Deploy Redis sliding-window rate limiters scoped by IP, Agent ID, and Tenant ID.

## Consequences & Trade-Offs
* **Benefits**: Instantly throttles high-frequency flood attempts with HTTP 429.
* **Trade-Offs**: Requires Redis lookup on ingress API requests.
