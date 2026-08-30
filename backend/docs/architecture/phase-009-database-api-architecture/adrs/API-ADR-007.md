# API-ADR-007: Standardized Internal Error Model JSON Response Format

## Context & Problem Statement
Unstandardized error responses confuse clients and risk leaking internal stack traces.

## Decision
Standardize on a fixed error JSON response format (`code`, `message`, `details`, `request_id`, `trace_id`).

## Consequences & Trade-Offs
* **Benefits**: Sanitizes sensitive internal stack traces while aiding debugging.
* **Trade-Offs**: Requires mapping internal exceptions to standard API errors.
