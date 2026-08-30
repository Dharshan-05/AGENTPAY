# AGENTPAY — 09: Agent Lifecycle Security & Credential Isolation

## 1. Agent Credential Isolation Boundaries

AI agents operate strictly via API keys and HMAC signatures. They possess zero access to raw banking tokens, credit card CVVs, or user PINs.

---

## 2. Revocation & Suspension SLA

* **Sub-10ms Purge**: Toggling an agent state to `REVOKED` or `SUSPENDED` purges Redis edge authentication keys in $< 10\text{ ms}$.
* **Immediate Edge Block**: Any request originating from a revoked agent key fails at Gateway Stage 1 with HTTP 403 `ERR_AGENT_REVOKED`.
* **Zero Residual Access**: Key hashes are purged; active sessions invalidated immediately.
