# AGENTPAY — 21: `apps/api` Express Application Structure & Bootstrapping

## 1. Startup Sequence

```
1. Load & Validate Environment Config (@agentpay/config)
2. Initialize Logger & OpenTelemetry Tracer (@agentpay/observability)
3. Test Database Pool & Redis Connections
4. Register Middleware (CORS, RateLimiter, Auth, TenantContext)
5. Register Domain API Routers (/payment-intents, /payments, /webhooks)
6. Start HTTP Server (Port 4000)
```
