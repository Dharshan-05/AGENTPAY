# AGENTPAY — 24: DoS / Velocity Abuse Defense & Circuit Breakers

## 1. Velocity Abuse & Circuit Breakers

To protect core banking rails from rapid-fire agent loops:

1. **Velocity Cap**: If an agent requests $> 5\text{ intents/sec}$, system automatically suspends the agent and emits security alert `ERR_VELOCITY_LIMIT_EXCEEDED`.
2. **Gateway Circuit Breaker**: If Razorpay API responds with 5 consecutive errors or timeouts ($> 5\text{s}$), circuit breaker opens for 30 seconds, returning `ERR_GATEWAY_CIRCUIT_OPEN`.
