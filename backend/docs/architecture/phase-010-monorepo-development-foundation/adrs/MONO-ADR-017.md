# MONO-ADR-017: Multi-Container Docker Compose Local Development Environment

## Context & Problem Statement
Providing a single command to spin up required infrastructure services (PostgreSQL, Redis) locally.

## Decision
Maintain root `docker-compose.yml` configured with PostgreSQL 15 and Redis 7 services, featuring health checks and automatic initialization scripts.

## Consequences & Trade-Offs
* **Benefits**: Rapid developer onboarding (`docker-compose up -d`).
* **Trade-Offs**: Developer must have Docker Desktop installed locally.
