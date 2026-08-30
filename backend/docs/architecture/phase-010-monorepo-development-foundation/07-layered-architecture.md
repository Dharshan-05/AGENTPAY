# AGENTPAY — 07: Layered Application Architecture (API -> Domain -> Data)

## 1. Backend Layering Standard

```
[ Ingress HTTP Controller ]
           │
           ▼
[ Application Service Layer ] (Orchestration, Auth Context)
           │
           ▼
[ Domain Model Layer ] (Payment Intent State Machine, Policy Rules)
           │
           ▼
[ Repository Infrastructure ] (PostgreSQL SQL Queries, Redis Cache)
```

Controllers do not contain raw SQL or direct database client calls. Domain logic is isolated from HTTP frameworks.
