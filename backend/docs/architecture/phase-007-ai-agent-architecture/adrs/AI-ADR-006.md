# AI-ADR-006: 6-Tier Prompt Hierarchy & XML Tag Isolation

## Context & Problem Statement
Adversarial prompt injection in untrusted web text can trick LLMs into overriding safety system instructions.

## Decision
Enforce a 6-Tier Prompt Hierarchy. System policy prompts take absolute precedence; untrusted external text is isolated within `<untrusted_content>` XML tags.

## Consequences & Trade-Offs
* **Benefits**: Neutralizes direct and indirect prompt injection attempts.
* **Trade-Offs**: Requires prompt pre-processing and sanitization middleware.
