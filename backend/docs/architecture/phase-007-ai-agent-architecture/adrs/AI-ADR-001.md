# AI-ADR-001: Modular Supervisor-Worker Multi-Agent Architecture

## Context & Problem Statement
Autonomous commerce requires specialized capabilities for intent parsing, cart assembly, fraud scoring, and payment validation. A monolithic single-prompt agent becomes unmaintainable and insecure.

## Decision
Adopt a modular supervisor-worker multi-agent architecture where a Supervisor Node orchestrates specialized Commerce, Payment, Security, Risk, and Support agents.

## Consequences & Trade-Offs
* **Benefits**: Isolates capabilities; enforces strict responsibility boundaries per agent type.
* **Trade-Offs**: Requires inter-agent message authorization protocols.
