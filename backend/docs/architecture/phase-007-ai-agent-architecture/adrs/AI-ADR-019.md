# AI-ADR-019: Zero-PII Prompt Redaction & Masking Protocol

## Context & Problem Statement
Dispatching raw user prompts containing credit cards, passwords, or phone numbers to external LLM provider APIs creates severe privacy violations.

## Decision
Execute automated regex PII masking on all prompt inputs prior to external model API dispatch, replacing sensitive data with `<REDACTED_CREDENTIAL>` tokens.

## Consequences & Trade-Offs
* **Benefits**: Guarantees zero sensitive user credentials reach third-party LLM providers.
* **Trade-Offs**: Requires lightweight regex scanning middleware on all outbound LLM requests.
