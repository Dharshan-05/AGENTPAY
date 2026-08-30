# AGENTPAY — 75: Multi-Layer API Gateway Security Controls

## 1. API Security Header Enforcement

All API HTTP responses include security headers:

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'none'
Cache-Control: no-store, max-age=0
```
