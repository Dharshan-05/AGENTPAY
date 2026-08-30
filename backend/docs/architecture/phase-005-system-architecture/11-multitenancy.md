# AGENTPAY — 11: Multi-Tenant Data & Application Isolation Architecture

## 1. Multi-Tenancy Architecture

AGENTPAY enforces strict tenant isolation across API middleware, database records, Redis caches, and event streams.

```mermaid
graph TD
    subgraph Shared Application Tier
        GW[API Gateway Middleware]
        TENANT_CONTEXT[Tenant Context Injector]
    end

    subgraph Data Isolation Tier
        subgraph Tenant A Workspace
            A_AGENTS[Tenant A Agents]
            A_POLICIES[Tenant A Policies]
            A_INTENTS[Tenant A Intents (tenant_id == A)]
        end
        subgraph Tenant B Workspace
            B_AGENTS[Tenant B Agents]
            B_POLICIES[Tenant B Policies]
            B_INTENTS[Tenant B Intents (tenant_id == B)]
        end
    end

    subgraph Datastore Isolation (Row-Level Security)
        PG_DB[(PostgreSQL Database)]
        REDIS_CACHE[(Redis Key Namespacing: tenant_id:agent_id)]
    end

    GW --> TENANT_CONTEXT
    TENANT_CONTEXT -->|Sets tenant_id in Session| A_AGENTS & B_AGENTS
    A_AGENTS & B_AGENTS --> PG_DB & REDIS_CACHE
```

---

## 2. Isolation Mechanisms

* **Database Row-Level Security (RLS)**: PostgreSQL tables enforce `WHERE tenant_id = current_setting('app.current_tenant')` policies.
* **Redis Key Namespacing**: Redis keys format as `<tenant_id>:<agent_id>:<key_name>`.
* **Zero Cross-Tenant Leakage**: Queries attempting to access data outside `tenant_id` context fail at the database driver boundary.
