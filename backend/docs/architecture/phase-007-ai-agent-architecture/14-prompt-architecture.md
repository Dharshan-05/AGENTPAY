# AGENTPAY — 14: 6-Tier System Prompt Hierarchy & Role Isolation

## 1. Prompt Hierarchy Structure

```
+-----------------------------------------------------------------------+
|                       6-TIER PROMPT HIERARCHY                         |
+-----------------------------------------------------------------------+
|  Tier 1: System Master Instructions (Immutable System Governance)      |
|  Tier 2: Security & Safety Policy (Deterministic Boundary Rules)      |
|  Tier 3: Agent Capability Scope (Assigned Scopes & Limits)            |
|  Tier 4: Task Execution Context (Active Goal & State)                 |
|  Tier 5: Human User Input (Authenticated User Request)                |
|  Tier 6: Untrusted External Content (Labeled Web/Merchant Data)       |
+-----------------------------------------------------------------------+
```

---

## 2. Role Boundary Enforcement

Tiers 1-3 are immutable system-level prompts injected by the backend runtime. Untrusted external web content (Tier 6) is strictly wrapped in `<untrusted_content>` tags, preventing external text from overriding Tiers 1-3 instructions.
