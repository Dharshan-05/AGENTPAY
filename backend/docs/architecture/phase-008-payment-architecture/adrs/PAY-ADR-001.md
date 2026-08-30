# PAY-ADR-001: Payment Orchestrator Component Boundary

## Context & Problem Statement
Exposing payment gateway APIs or credentials to AI agents or web frontends introduces unacceptable financial security risks.

## Decision
Establish the Payment Orchestrator as the exclusive internal service boundary authorized to interact with payment provider adapters.

## Consequences & Trade-Offs
* **Benefits**: Isolates gateway credentials; guarantees that all transactions undergo policy authorization.
* **Trade-Offs**: Requires all payment requests to route through the orchestrator service.
