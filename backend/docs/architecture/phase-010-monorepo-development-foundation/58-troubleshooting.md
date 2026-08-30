# AGENTPAY — 58: Developer Troubleshooting FAQ & Common Error Fixes

## 1. Frequently Encountered Issues

* **Postgres Connection Refused**: Run `docker-compose ps` to verify postgres container is healthy. Reset via `docker-compose restart postgres`.
* **TypeScript Circular Imports**: Run `pnpm lint` to pinpoint circular import paths between `@agentpay` workspace modules.
* **Idempotency Conflict (409)**: Clear Redis cache via `docker-compose exec redis redis-cli FLUSHALL`.
