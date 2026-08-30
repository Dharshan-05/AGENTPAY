# API-ADR-019: Backward-Compatible Contract Evolution & Deprecation Headers

## 1. Context & Problem Statement
Evolving API endpoints without disrupting active mobile app or web frontend clients.

## 2. Decision
Enforce additive, backward-compatible schema changes within major version paths (`/api/v1/`). Deprecated endpoints return `Sunset` HTTP headers.

## Consequences & Trade-Offs
* **Benefits**: Smooth migration path for API consumers.
* **Trade-Offs**: Deprecated fields must remain supported until major version sunset.
