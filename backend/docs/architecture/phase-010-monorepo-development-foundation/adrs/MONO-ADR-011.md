# MONO-ADR-011: Encapsulated Database Package (`@agentpay/database`)

## Context & Problem Statement
Preventing application microservices from building duplicate database connection pools or SQL query builders.

## Decision
Centralize PostgreSQL client pool creation, TypeORM/Prisma DDL schemas, and repository base classes in `@agentpay/database`.

## Consequences & Trade-Offs
* **Benefits**: Single location for database connection management and migration governance.
* **Trade-Offs**: All services importing `@agentpay/database` depend on its build lifecycle.
