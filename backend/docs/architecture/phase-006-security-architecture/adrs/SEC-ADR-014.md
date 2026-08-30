# SEC-ADR-014: Privileged Access Step-Up Authentication

## Context & Problem Statement
Administrative functions (e.g. changing global risk thresholds, disengaging Emergency Stop) carry extreme systemic risk.

## Threat Analysis
An attacker acquiring an active admin session token could execute high-impact configuration changes without re-authenticating.

## Decision
Require mandatory Step-Up Authentication (Password re-entry + TOTP MFA code) prior to processing any privileged administrative change.

## Consequences & Trade-Offs
* **Benefits**: Prevents session hijacking from escalating into systemic configuration tampering.
* **Trade-Offs**: Adds re-authentication friction for administrative users.
