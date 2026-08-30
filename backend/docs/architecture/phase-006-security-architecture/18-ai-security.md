# AGENTPAY — 18: Prompt Injection Defense & Untrusted Content Isolation

## 1. AI Threat Defense Architecture

```
[ External Untrusted Text (Merchant Desc, Web Pages, Tool Output) ]
                                │
                                ▼
[ 1. Context Sanitization & System Prompt Separation ]
                                │
                                ▼
[ 2. LLM Intent & Parameter Output Generation ]
                                │
                                ▼
[ 3. Hard JSON Schema & Type Validation ]
                                │
                                ▼
[ 4. Mandatory AGENTGUARD Policy & Risk Evaluation Gate ] ──(Breached)──> BLOCK
                                │
                                ▼ (Safe)
[ 5. Payment Execution Adapter ]
```

---

## 2. Prompt Injection Safeguards

* **Strict Input Separation**: System policy instructions and untrusted external user text are maintained in strictly isolated prompt roles (`system` vs `user`).
* **External Security Gate Supremacy**: LLM reasoning module cannot execute payments directly. AGENTGUARD evaluates policy caps independently outside the LLM execution context.
