# SEC-ADR-017: Multi-Tier Emergency Payment Kill Switch

## Context & Problem Statement
During systemic market anomalies, zero-day exploits, or gateway breaches, operators must possess the ability to freeze payments instantly.

## Threat Analysis
A widespread prompt injection vulnerability could cause thousands of agents to initiate unauthorized transactions simultaneously.

## Decision
Architect four independent, server-side Emergency Kill Switches (Global, Tenant, Agent, Merchant) propagating flags in $< 100\text{ ms}$ via Redis.

## Consequences & Trade-Offs
* **Benefits**: Instant circuit-breaking mechanism to protect platform liquidity.
* **Trade-Offs**: Requires privileged authorization and fail-closed state handling.
