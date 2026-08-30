# AGENTPAY — 50: REST API URI Path Versioning (`/api/v1/...`) Strategy

## 1. URI Path Versioning Strategy

All public and internal API endpoints enforce URI path versioning:

```
https://api.agentpay.com/api/v1/payment-intents
```

---

## 2. Deprecation & Migration Policy

* **Breaking Changes**: Banned within a major version (`v1`). Introduced exclusively under a new major path (`/api/v2/`).
* **Deprecation Header**: Deprecated endpoints return HTTP `Sunset: Wed, 11 Nov 2026 00:00:00 GMT` header signaling deprecation timeline.
