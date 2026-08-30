# AGENTPAY — Master State Machines Specification

## 1. Overview

This document specifies the four primary state machines governing entity lifecycles within AGENTPAY: **Agent Lifecycle**, **Payment Intent**, **Human Approval**, and **Transaction Risk Evaluation**.

---

## 2. Agent Lifecycle State Machine

```
       +--------------------+
       |     REGISTERED     | (Credentials issued, awaiting initial policy set)
       +--------------------+
                 │
                 ▼ (Owner configures initial policy)
       +--------------------+
       |       ACTIVE       | <=======> +--------------------+
       +--------------------+           |       PAUSED       | (Owner manual pause)
                 │                      +--------------------+
                 ├─── (Security alert / High risk violation) ──────────┐
                 │                                                      ▼
                 ├─── (Owner Emergency Stop triggered) ────────> +--------------------+
                 │                                              |     SUSPENDED      |
                 │                                              +--------------------+
                 ▼ (Owner hard revocation)                                │
       +--------------------+                                            │
       |      REVOKED       | <──────────────────────────────────────────┘
       +--------------------+ (Terminal State: Key hash purged, API calls fail)
```

### Transition Table

| Current State | Target State | Trigger Event | Allowed Actor | Preconditions |
| :--- | :--- | :--- | :--- | :--- |
| `REGISTERED` | `ACTIVE` | Initial Policy Saved | USER | Policy rules configured |
| `ACTIVE` | `PAUSED` | Pause Agent Clicked | USER | User active session |
| `PAUSED` | `ACTIVE` | Resume Agent Clicked| USER | User active session |
| `ACTIVE` | `SUSPENDED` | Emergency Stop | USER / SYSTEM | Alert or Kill switch triggered |
| `PAUSED` | `SUSPENDED` | Emergency Stop | USER / SYSTEM | Alert or Kill switch triggered |
| `ANY` | `REVOKED` | Revoke Agent Clicked| USER | User active session |

*Forbidden Transitions*: `REVOKED` $\rightarrow$ Any State (Terminal State).

---

## 3. Payment Intent State Machine

```
               +-------------------+
               |      CREATED      |
               +-------------------+
                         │
                         ▼ (Passed Schema & Auth Validation)
               +-------------------+
               |     POLICIED      |
               +-------------------+
                         │
                         ▼ (Passed FraudGuard Risk Scoring)
               +-------------------+
               |      SCORED       |
               +-------------------+
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
+---------------+ +--------------+ +---------------+
|   AUTHORIZED  | |PENDING_APP...| |   REJECTED    | (Terminal Failure)
+---------------+ +--------------+ +---------------+
        │                │
        │                ▼ (Human User Approves)
        │         +--------------+
        └────────>|  PROCESSING  |
                  +--------------+
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
+---------------+                 +---------------+
|   EXECUTED    |                 |    FAILED     | (Terminal Execution Failure)
+---------------+                 +---------------+
(Terminal Success)
```

### Transition Table

| Current State | Target State | Trigger Event | Allowed Actor | Preconditions |
| :--- | :--- | :--- | :--- | :--- |
| `CREATED` | `POLICIED` | AGENTGUARD Checks Pass | SYSTEM | Auth & Schema Validated |
| `CREATED` | `BLOCKED` | AGENTGUARD Limit Exceeded| SYSTEM | Policy Rule Violation |
| `POLICIED` | `SCORED` | FRAUDGUARD Score Done | SYSTEM | Feature Extraction Complete |
| `SCORED` | `AUTHORIZED` | Low Risk / Under Ceiling| SYSTEM | Decision == ALLOW |
| `SCORED` | `PENDING_APP` | Exceeds Auto-Ceiling | SYSTEM | Decision == REVIEW |
| `PENDING_APP` | `AUTHORIZED` | User Clicks Approve | USER | Active User Session |
| `PENDING_APP` | `REJECTED` | User Clicks Reject | USER | Active User Session |
| `PENDING_APP` | `EXPIRED` | 15m Timeout Elapsed | SYSTEM | No User Action in 15m |
| `AUTHORIZED` | `PROCESSING` | Payment Service Call | SYSTEM | Valid Auth Signature |
| `PROCESSING` | `EXECUTED` | Gateway Settlement OK | SYSTEM | Processor Code == SUCCESS |
| `PROCESSING` | `FAILED` | Gateway Timeout/Error| SYSTEM | Processor Code != SUCCESS |
