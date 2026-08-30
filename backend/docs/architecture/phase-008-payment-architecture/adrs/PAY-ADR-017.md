# PAY-ADR-017: FRAUDGUARD ML Risk Score Interception Gate

## 1. Context & Problem Statement
Static payment rules cannot detect complex adversarial transaction anomalies or fraud patterns.

## 2. Decision
Integrate FRAUDGUARD Python XGBoost ML risk scoring into the AGENTGUARD policy check flow prior to issuing authorization tokens.

## 3. Consequences & Trade-Offs
* **Benefits**: Real-time fraud detection with sub-30ms execution SLA.
* **Trade-Offs**: Outages must fail closed to `REVIEW` status.
