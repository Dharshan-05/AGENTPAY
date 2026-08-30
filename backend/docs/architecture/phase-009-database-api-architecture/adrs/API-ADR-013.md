# API-ADR-013: Modular Domain Monolith Microservice Service Boundaries

## 1. Context & Problem Statement
Preventing premature microservice splitting overhead while maintaining clean domain boundaries.

## 2. Decision
Structure backend code as a Modular Monolith with clear internal domain service boundaries (Identity, Payment, Policy, Risk).

## 3. Consequences & Trade-Offs
* **Benefits**: Simplifies deployment while preserving clear future microservice extraction boundaries.
* **Trade-Offs**: Requires enforcing module dependency rules in code reviews.
