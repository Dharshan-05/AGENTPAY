# MONO-ADR-020: Independent AGENTGUARD Security Control Plane (`apps/agentguard`)

## 1. Context & Problem Statement
Preventing autonomous agent reasoning models from bypassing security policies or executing unauthorized payments.

## 2. Decision
Deploy AGENTGUARD as an independent microservice (`apps/agentguard`), enforcing 6-stage policy verification, FRAUDGUARD risk scoring, and issuing signed payment authorizations.

## 3. Consequences & Trade-Offs
* **Benefits**: 100% zero-trust guarantee; LLMs cannot bypass security policies.
* **Trade-Offs**: Introduces an internal microservice evaluation hop before payment authorization.
