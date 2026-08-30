# AGENTPAY API Traffic Readiness Endpoint Architecture

## Overview & Purpose

The AGENTPAY backend service (`apps/agent-runtime`) provides a dedicated traffic readiness endpoint (`GET /api/v1/ready`) designed for container orchestrators (Kubernetes, Docker), service meshes, and load balancers.

The readiness endpoint answers one fundamental question: **Is the AGENTPAY application ready to receive normal production traffic?**

---

## Health vs. Readiness Semantics

- **Phase 026 — Process Liveness (`GET /api/v1/health`)**:
  - Evaluates whether the Python process, ASGI application, event loop, and HTTP stack are functioning.
  - Performs zero external dependency checks.
  - Failure results in pod **restarts**.
- **Phase 027 — API Readiness (`GET /api/v1/ready`)**:
  - Evaluates whether the application initialization and required downstream integrations are ready to process traffic.
  - Failure results in removing the container instance from active load balancer traffic pools without restarting the process.

---

## Response Contracts

### READY Response (HTTP 200 OK)

```http
GET /api/v1/ready HTTP/1.1
Host: api.agentpay.com
X-Request-ID: ready-check-202
```

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: ready-check-202

{
  "success": true,
  "data": {
    "status": "ready"
  },
  "meta": {
    "request_id": "ready-check-202"
  }
}
```

### NOT READY Response (HTTP 503 Service Unavailable)

```http
GET /api/v1/ready HTTP/1.1
Host: api.agentpay.com
X-Request-ID: ready-check-503
```

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
X-Request-ID: ready-check-503

{
  "success": false,
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service is not ready.",
    "details": null
  },
  "meta": {
    "request_id": "ready-check-503"
  }
}
```

---

## Readiness Abstraction Architecture

The readiness architecture separates API transport from readiness evaluation logic:

```text
       GET /api/v1/ready
               ↓
    API Controller (app/api/v1/ready.py)
               ↓
  ReadinessService (app/application/services/readiness.py)
               ↓
    ReadinessCheck Registry
    ├── ApplicationReadinessCheck (Lifecycle & Config)
    ├── [Future] DatabaseReadinessCheck (PostgreSQL)
    └── [Future] RedisReadinessCheck (Cache/Locks)
               ↓
    Aggregate Status (READY / NOT_READY)
```

### Fail-Closed & Bounded Execution Policy

- **Fail-Closed Safety**: If any registered readiness check fails, throws an unhandled exception, or times out, the service immediately evaluates as `NOT_READY` and returns HTTP 503.
- **Bounded Timeout**: All checks execute within configurable execution timeout bounds (`default_timeout_seconds=2.0`).

---

## Orchestration Configuration

### Kubernetes Probe Configuration

```yaml
readinessProbe:
  httpGet:
    path: /api/v1/ready
    port: 8000
    httpHeaders:
      - name: X-Request-ID
        value: k8s-readiness-probe
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

---

## Security & Confidentiality

To prevent information disclosure:
- No database credentials, Redis connection strings, passwords, tokens, or API keys are exposed.
- Stack traces, internal exception details, and filesystem paths are omitted from HTTP 503 payloads.
- Structured logs record internal diagnostics (`readiness.check`) securely without exposing secrets.
