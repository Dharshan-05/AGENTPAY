# AGENTPAY — 38: Multi-Model Fallback & State Preservation Protocols

## 1. Fallback State Preservation

When failover occurs from the primary model (`gpt-4o`) to the secondary model (`claude-3-5-sonnet`) due to API timeout or rate limiting, the agent state checkpoint preserved in Redis is reloaded, ensuring zero side-effect duplication or double payment proposals.
