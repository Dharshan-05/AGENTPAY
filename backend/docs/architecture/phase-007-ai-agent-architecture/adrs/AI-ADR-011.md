# AI-ADR-011: Mandatory AGENTGUARD Interception Gate

## Context & Problem Statement
AI agents proposing payment intents could attempt to execute transactions exceeding spending policies.

## Decision
Mandate AGENTGUARD as an independent security control plane that evaluates 6-stage policy rules on every payment intent proposal prior to Payment Orchestrator settlement dispatch.

## Consequences & Trade-Offs
* **Benefits**: Prevents unauthorized autonomous fund transfers.
* **Trade-Offs**: Adds ~15ms inter-service evaluation call.
