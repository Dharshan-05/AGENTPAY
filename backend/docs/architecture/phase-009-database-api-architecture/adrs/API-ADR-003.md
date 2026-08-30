# API-ADR-003: Multi-Actor Ingress Authentication Strategy

## Context & Problem Statement
A single authentication mechanism cannot securely serve human users, AI agents, and internal microservices.

## Decision
Support multi-actor authentication: OAuth2 JWT for users, HMAC-SHA256 request signatures for AI agents, mTLS for internal services.

## Consequences & Trade-Offs
* **Benefits**: Secures each actor type with purpose-built cryptographic controls.
* **Trade-Offs**: Requires authentication middleware for each actor path.
