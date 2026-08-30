# AGENTPAY — 15: Trust Boundaries, Threat Modeling & Defense-in-Depth

## 1. Trust Boundary Diagram

```
[ UNTRUSTED INTERNET ]
        │
        ▼ (Boundary 1: TLS 1.3 / HMAC Verification)
[ API GATEWAY EDGE ]
        │
        ▼ (Boundary 2: Internal JWT / Mutual TLS)
[ AGENTPAY MICROSERVICES ]
        │
        ▼ (Boundary 3: RLS / Database Credentials)
[ DATASTORE & AUDIT LOGS ]
        │
        ▼ (Boundary 4: Razorpay API Signatures)
[ EXTERNAL RAZORPAY RAILS ]
```

---

## 2. Boundary Controls

* **Boundary 1 (Edge)**: Enforces HMAC-SHA256 request authentication, replay nonce caching, and IP rate limiting.
* **Boundary 2 (Internal Services)**: Internal mTLS / scoped JWT tokens prevent unauthorized service-to-service calls.
* **Boundary 3 (Datastore)**: Database connection pooling with restricted user roles; PostgreSQL RLS policies; Argon2id hashed credentials.
* **Boundary 4 (External Razorpay)**: Webhook HMAC signature validation (`X-Razorpay-Signature`); isolated payment tokens.
