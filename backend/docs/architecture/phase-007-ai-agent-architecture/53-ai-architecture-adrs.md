# AGENTPAY — 53: Index of 20 AI Architecture Decision Records (`adrs/`)

## 1. ADR Summary Index

| ADR ID | Title | Core Decision Summary |
| :--- | :--- | :--- |
| **AI-ADR-001**| Agent Architecture | Modular, supervisor-worker multi-agent architecture |
| **AI-ADR-002**| Agent Identity Separation | Decouple Agent Principal identity (`agent_id`) from LLM model |
| **AI-ADR-003**| Agent Orchestration | LangGraph state machine graph for agent flow control |
| **AI-ADR-004**| Model Abstraction | Abstract `ILLMProvider` interface for multi-vendor routing |
| **AI-ADR-005**| Model Routing | Dynamic task routing (fast/reasoning LLMs, XGBoost ML) |
| **AI-ADR-006**| Prompt Architecture | 6-Tier System Prompt hierarchy & XML tag isolation |
| **AI-ADR-007**| Memory Architecture | Segregated short-term (Redis) & long-term (PostgreSQL) memory |
| **AI-ADR-008**| RAG Architecture | PostgreSQL + pgvector cosine similarity search |
| **AI-ADR-009**| Tool Architecture | Centralized Tool Registry with Zod JSON Schema validation |
| **AI-ADR-010**| Tool Authorization | Capability scope check prior to tool execution |
| **AI-ADR-011**| AGENTGUARD Integration | Mandatory external policy gate intercept for payment proposals |
| **AI-ADR-012**| Hybrid AI + Rules | LLM reasoning + Deterministic rules + XGBoost ML scoring |
| **AI-ADR-013**| Explainable AI | SHAP feature attributions & natural text synthesis |
| **AI-ADR-014**| Human-in-the-Loop | 15-minute TTL escalation cards in Approval Center |
| **AI-ADR-015**| Multi-Agent Architecture | Hierarchical supervisor topology with isolated workers |
| **AI-ADR-016**| AI Observability | OpenTelemetry W3C distributed tracing & token metrics |
| **AI-ADR-017**| AI Evaluation | Offline precision benchmarks & 40 injection attack tests |
| **AI-ADR-018**| AI Failure Recovery | Fail-closed security fallbacks on LLM/ML outages |
| **AI-ADR-019**| AI Privacy | Regex PII scrubbing prior to external API dispatch |
| **AI-ADR-020**| Autonomous Payment Boundary| LLM cannot directly call Razorpay APIs |
