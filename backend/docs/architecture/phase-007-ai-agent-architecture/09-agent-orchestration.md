# AGENTPAY — 09: LangGraph / LangChain Agent Orchestration Engine

## 1. Orchestration Engine Blueprint

AGENTPAY uses LangGraph state machine graphs for deterministic agent orchestration.

```mermaid
graph TD
    START[Task Request] --> PLAN[1. Planner Node]
    PLAN --> ROUTE{2. Model Router}
    ROUTE --> LLM[3. LLM Reasoning Node]
    LLM --> VALIDATE{4. Plan Schema Validation}
    VALIDATE -- Invalid --> PLAN
    VALIDATE -- Valid --> TOOL_GATE{5. Tool Capability Check}
    TOOL_GATE -- Denied --> FAIL[Reject Action]
    TOOL_GATE -- Approved --> TOOL_EXEC[6. Tool Execution Node]
    TOOL_EXEC --> GUARD_GATE{7. AGENTGUARD Security Intercept}
    GUARD_GATE -- ALLOW --> PAY[8. Payment Orchestration Node]
    GUARD_GATE -- REVIEW --> HUMAN[Escalate to Approval Center]
    GUARD_GATE -- BLOCK --> REJECT[Block Execution]
```

---

## 2. Framework Isolation Rule

The orchestration framework (LangGraph) functions exclusively as a flow control mechanism. It possesses zero authority to grant policy permissions or execute payments directly. All financial authorization remains externalized in AGENTGUARD.
