# AGENTPAY API Process Liveness Health Endpoint Architecture

## Overview & Purpose

The AGENTPAY backend service (`apps/agent-runtime`) provides a dedicated process liveness health endpoint (`GET /api/v1/health`) designed for container orchestrators, load balancers, and enterprise SRE monitoring.

The health endpoint answers one fundamental question: **Is the AGENTPAY application process alive and capable of receiving and processing HTTP requests?**

---

## Canonical Response Contract

```http
GET /api/v1/health HTTP/1.1
Host: api.agentpay.com
X-Request-ID: health-check-101
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: health-check-101

{
  "success": true,
  "data": {
    "status": "healthy"
  },
  "meta": {
    "request_id": "health-check-101"
  }
}
```

---

## Liveness vs. Readiness Semantics

- **Phase 026 — Process Liveness (`GET /api/v1/health`)**:
  - Evaluates whether the Python process, ASGI application, event loop, and HTTP stack are functioning.
  - Performs **zero external dependency checks** (no PostgreSQL, Redis, external APIs, message brokers, or disk writes).
  - **Reason**: A liveness probe failure causes container orchestrators (e.g. Kubernetes, AWS ECS) to **restart** the container pod. If external dependencies (like PostgreSQL or Redis) experience temporary degradation, restarting healthy application containers creates cascading outages.
- **Phase 027 — API Readiness (`GET /api/v1/readiness`)**:
  - Evaluates whether downstream dependencies are connected and ready to serve live traffic.
  - Used by load balancers to temporarily remove instance targets from active traffic pools without restarting processes.

---

## Orchestration Configuration

### Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
    httpHeaders:
      - name: X-Request-ID
        value: k8s-liveness-probe
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

---

## Security & Minimal Exposure Boundary

To prevent operational intelligence leakage, the public health response intentionally omits:
- Hostnames or IP addresses
- Process IDs (PID)
- Python / OS framework versions
- Database / Redis connectivity status
- Environment variables or secrets

---

## Pipeline & Middleware Integration

The health endpoint automatically integrates with:
- **Request ID Middleware (`app/middleware/request_id.py`)**: Accepts or generates `X-Request-ID`.
- **Response Standardization (`app/middleware/response.py`)**: Formats payloads into canonical `SuccessResponse`.
- **CORS Configuration (`app/middleware/registration.py`)**: Applies origin rules and exposes `X-Request-ID`.
- **API Middleware (`app/middleware/api.py`)**: Emits structured HTTP request lifecycle logs (`event="http.request"`).
