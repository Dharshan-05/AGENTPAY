# AGENTPAY — 04: Application Domain Boundaries & Scope Specification

## 1. Application Directory Breakdown

* `apps/web`: React / Next.js frontend serving human user dashboards, approval card reviews, and merchant management.
* `apps/api`: Primary REST API microservice exposing public endpoints, authentication, and payment orchestration.
* `apps/agent-runtime`: Python FastAPI application housing autonomous agent reasoning loops, tool dispatch, and LLM integrations.
* `apps/agentguard`: Independent security decision microservice evaluating policy rules, trust scores, and issuing authorization tokens.
* `apps/worker`: Background Node.js process polling `outbox_events`, executing webhooks, and processing async reconciliation tasks.
