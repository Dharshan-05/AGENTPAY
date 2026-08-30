# AGENTPAY — 32: Compromised Agent Containment & Credential Freeze

## 1. Compromised Agent Containment Protocol

When an AI AGENT is flagged for anomalous velocity, prompt injection exploit attempts, or high risk scores ($> 90$):

1. **Instant Suspension**: AGENTGUARD updates agent state to `SUSPENDED`.
2. **Edge Cache Purge**: Redis edge authentication keys evicted ($< 10\text{ ms}$).
3. **Pending Intent Cancellation**: All pending intents in `PENDING_APPROVAL` status canceled automatically.
4. **Owner Push Notification**: Human account owner notified immediately via push alert.
5. **Key Invalidation**: HMAC secret key marked `EXPIRED` requiring manual user key re-issuance.
