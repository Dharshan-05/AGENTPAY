# AGENTPAY — 51: AI Trust Boundaries & Security Enforcement Points

## 1. Trust Boundaries Diagram

```
[ UNTRUSTED EXTERNAL WEB / MERCHANT DATA ]
                    │
                    ▼ (Boundary 1: Prompt Sanitizer & Role Isolation)
[ LLM REASONING & AGENT PLANNER CONTAINER ]
                    │
                    ▼ (Boundary 2: Pydantic Schema & Capability Scope Check)
[ AGENTGUARD POLICY & SECURITY CONTROL PLANE ]
                    │
                    ▼ (Boundary 3: Cryptographic Token & Authorization ID)
[ PAYMENT ORCHESTRATOR & RAZORPAY ADAPTER ]
```

The LLM operates strictly inside Boundary 1. It cannot cross Boundary 2 without deterministic AGENTGUARD policy authorization.
