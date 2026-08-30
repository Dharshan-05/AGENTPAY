# AGENTPAY — 15: Direct & Indirect Prompt Injection Defense Pipeline

## 1. Multi-Layered Injection Defense

```
[ External Untrusted Content ] ──> [ Sanitizer ] ──> [ Delimiter Tagging ] ──> [ LLM Generation ] ──> [ AGENTGUARD Gate ] ──> [ Output ]
```

---

## 2. Security Safeguards

1. **Context Isolation**: External text parsed from merchant descriptions or web search tools is wrapped inside `<untrusted_data>` XML blocks.
2. **Schema Sanitization**: Regex patterns scrub dangerous instruction strings (`"Ignore previous instructions"`, `"System override"`).
3. **AGENTGUARD Supremacy**: Even if an LLM is hijacked by an adversarial prompt, the resulting payment proposal is blocked deterministically at the AGENTGUARD policy boundary.
