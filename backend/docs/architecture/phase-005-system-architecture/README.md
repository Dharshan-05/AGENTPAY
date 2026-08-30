# AGENTPAY + AGENTGUARD — System Architecture Specification (Phase 005)

## Executive Summary

This directory contains the authoritative, production-grade **System Architecture Specification** for **AGENTPAY** (Autonomous Agent Commerce Infrastructure), **AGENTGUARD** (Trusted AI Agent Policy, Security & Authorization Control Plane), and **FRAUDGUARD** (Explainable AI Fraud & Risk Engine).

Designed for high-stakes autonomous agentic commerce, this architecture bridges the critical trust gap between machine-speed AI agents and financial payment execution. It guarantees that machine-initiated transactions are cryptographically authenticated, policy-bounded, risk-evaluated, human-explainable, auditable, and payment-safe.

---

## Document Index

| Index | Document Title | Description |
| :--- | :--- | :--- |
| **01** | [`01-system-context.md`](01-system-context.md) | System Context Diagram & Boundary Specifications |
| **02** | [`02-high-level-architecture.md`](02-high-level-architecture.md) | 9-Layer Logical System Architecture |
| **03** | [`03-component-architecture.md`](03-component-architecture.md) | Microservices & Component Structural Specifications |
| **04** | [`04-agentpay-architecture.md`](04-agentpay-architecture.md) | AGENTPAY Core Autonomous Agent Commerce Architecture |
| **05** | [`05-agentguard-architecture.md`](05-agentguard-architecture.md) | AGENTGUARD Security Control Plane & Policy Engine |
| **06** | [`06-payment-flow.md`](06-payment-flow.md) | Payment Orchestrator & Razorpay Gateway Boundary |
| **07** | [`07-transaction-state-machine.md`](07-transaction-state-machine.md) | 14-State Transaction State Machine Specification |
| **08** | [`08-risk-decision-architecture.md`](08-risk-decision-architecture.md) | FRAUDGUARD 12-Dimensional Risk Engine & XAI Pipeline |
| **09** | [`09-event-driven-architecture.md`](09-event-driven-architecture.md) | Asynchronous Event Bus, Pub/Sub & DLQ Architecture |
| **10** | [`10-data-flow.md`](10-data-flow.md) | Data Flow & Cryptographic Audit Block Hash Pipeline |
| **11** | [`11-multitenancy.md`](11-multitenancy.md) | Multi-Tenant Data & Application Isolation Architecture |
| **12** | [`12-scalability.md`](12-scalability.md) | Horizontal Stateless Worker & Datastore Scaling Strategy |
| **13** | [`13-high-availability.md`](13-high-availability.md) | Multi-Region Availability & Redundancy Specifications |
| **14** | [`14-resilience.md`](14-resilience.md) | Circuit Breakers, Rate Limiters & Graceful Degradation |
| **15** | [`15-security-boundaries.md`](15-security-boundaries.md) | Trust Boundaries, Threat Modeling & Defense-in-Depth |
| **16** | [`16-observability.md`](16-observability.md) | Structured JSON Logs, OpenTelemetry & Prometheus Tracing |
| **17** | [`17-deployment.md`](17-deployment.md) | Docker & Kubernetes Container Deployment Topology |
| **18** | [`18-technology-boundaries.md`](18-technology-boundaries.md) | Production Tech Stack Selection & Justification Matrix |
| **19** | [`19-architecture-decisions.md`](19-architecture-decisions.md) | Master Architecture Decision Records (ADR-001 to ADR-012)|
| **20** | [`20-failure-recovery.md`](20-failure-recovery.md) | Component Outage Playbooks & Automatic Cache Recovery |

---

## Mermaid Diagram Library (`diagrams/`)

1. [`01-system-context.mmd`](diagrams/01-system-context.mmd)
2. [`02-high-level-architecture.mmd`](diagrams/02-high-level-architecture.mmd)
3. [`03-component-architecture.mmd`](diagrams/03-component-architecture.mmd)
4. [`04-agent-execution-flow.mmd`](diagrams/04-agent-execution-flow.mmd)
5. [`05-agentguard-security-flow.mmd`](diagrams/05-agentguard-security-flow.mmd)
6. [`06-payment-flow.mmd`](diagrams/06-payment-flow.mmd)
7. [`07-transaction-state-machine.mmd`](diagrams/07-transaction-state-machine.mmd)
8. [`08-risk-decision-pipeline.mmd`](diagrams/08-risk-decision-pipeline.mmd)
9. [`09-human-approval-flow.mmd`](diagrams/09-human-approval-flow.mmd)
10. [`10-event-driven-architecture.mmd`](diagrams/10-event-driven-architecture.mmd)
11. [`11-data-flow-architecture.mmd`](diagrams/11-data-flow-architecture.mmd)
12. [`12-multi-tenant-architecture.mmd`](diagrams/12-multi-tenant-architecture.mmd)
13. [`13-deployment-architecture.mmd`](diagrams/13-deployment-architecture.mmd)
14. [`14-failure-recovery-architecture.mmd`](diagrams/14-failure-recovery-architecture.mmd)
15. [`15-observability-architecture.mmd`](diagrams/15-observability-architecture.mmd)
