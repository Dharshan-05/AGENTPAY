# AGENTPAY — 43: Autonomous Agent Prompt Injection & Policy Bypass Test Suite

## 1. Agent Security Tests

* **Prompt Injection Defense**: Submits malicious prompt injection in order item description; verifies AGENTGUARD policy engine block.
* **Capability Boundary Test**: Agent attempts to invoke payment intent without `spend:intent_create` scope; verifies HTTP 403 Forbidden rejection.
