# MONO-ADR-015: Multi-Tier Testing Pyramid Architecture

## Context & Problem Statement
Balancing test execution speed with end-to-end financial transaction verification.

## Decision
Implement a 3-tier testing pyramid: Fast Vitest unit tests (60%), Supertest integration tests against Docker Postgres (30%), Playwright E2E tests (10%).

## Consequences & Trade-Offs
* **Benefits**: Rapid local feedback loop while maintaining high confidence in critical financial paths.
* **Trade-Offs**: Integration and E2E tests require running containerized databases.
