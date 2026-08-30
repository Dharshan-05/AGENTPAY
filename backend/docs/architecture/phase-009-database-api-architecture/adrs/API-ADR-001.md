# API-ADR-001: Resource-Oriented RESTful API Architecture

## Context & Problem Statement
Exposing arbitrary RPC or unstandardized endpoints creates API maintenance confusion.

## Decision
Adopt standard resource-oriented RESTful API endpoints with explicit HTTP verbs (`GET`, `POST`, `DELETE`).

## Consequences & Trade-Offs
* **Benefits**: Predictable, intuitive API contracts matching OpenAPI standards.
* **Trade-Offs**: Complex operations require explicit command endpoints (`/authorize`).
