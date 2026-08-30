# API-ADR-005: Trusted Server-Side Tenant Context Resolution

## Context & Problem Statement
Trusting `tenant_id` query parameters or JSON body fields allows cross-tenant spoofing.

## Decision
Extract `tenant_id` exclusively from verified server-side JWT claims or HMAC agent keys, ignoring client-supplied headers.

## Consequences & Trade-Offs
* **Benefits**: Guarantees zero tenant context forgery.
* **Trade-Offs**: Requires attaching tenant IDs to authenticated token claims.
