# AGENTPAY — 14: Circuit Breakers, Rate Limiters & Graceful Degradation Architecture

## 1. Resilience Patterns

AGENTPAY embeds defense-in-depth resilience patterns across all microservice communication boundaries.

---

## 2. Pattern Specifications

### 2.1 Circuit Breaker (Razorpay API Boundary)
* **Trigger**: 5 consecutive settlement API timeouts ($> 5,000\text{ ms}$) or 5xx gateway errors within 60s.
* **Action**: Circuit opens for 30s; immediate fail-fast return of `ERR_GATEWAY_CIRCUIT_OPEN`.
* **Reset**: Half-open trial call after 30s reset timeout.

### 2.2 Rate Limiter (Edge API Gateway)
* **Limits**: 60 requests/minute per agent; 120 requests/minute per IP address.
* **Mechanism**: Redis sliding window counter.
* **Exceeded Action**: HTTP 429 `Too Many Requests`.

### 2.3 Fail-Safe Degradation
* **Rule**: Internal service errors (e.g. ML container timeout) NEVER default to `ALLOW`. System defaults to `BLOCK` or `REVIEW`.
