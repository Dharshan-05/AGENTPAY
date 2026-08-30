# AI-ADR-017: Offline Precision Benchmarks & 40 Injection Tests

## Context & Problem Statement
Deploying un-evaluated prompt changes risks introducing regression bugs or prompt injection vulnerabilities.

## Decision
Mandate automated execution of an evaluation suite covering 40 prompt injection attack vectors and synthetic fraud datasets prior to deploying any prompt or model update.

## Consequences & Trade-Offs
* **Benefits**: Guarantees zero regression on prompt injection defenses.
* **Trade-Offs**: Extends CI/CD build execution time by ~2 minutes.
