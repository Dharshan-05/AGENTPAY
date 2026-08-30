# API-ADR-020: Fail-Closed Gateway Circuit Breakers & Outage Degradation

## 1. Context & Problem Statement
Handling downstream microservice outages (e.g. FRAUDGUARD ML container failure, database connection drop).

## 2. Decision
Enforce fail-closed circuit breaking; if risk or policy services fail, ingress API returns HTTP 503 Service Temporarily Unavailable, blocking payments.

## Consequences & Trade-Offs
* **Benefits**: 100% protection against financial leakage during microservice outages.
* **Trade-Offs**: System temporarily holds or rejects intents during upstream outages.
