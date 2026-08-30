# AGENTPAY — 06: Monorepo Package Dependency Direction Rules

## 1. Strict Dependency Direction

```
apps/*  ──>  packages/* (Domain/Infra)  ──>  packages/types & config
```

* **Rule 1**: `apps/*` can import `@agentpay/*` packages.
* **Rule 2**: `packages/*` CANNOT import from `apps/*`.
* **Rule 3**: `packages/types` has ZERO dependencies on other internal packages.
* **Rule 4**: Circular dependencies between packages are forbidden and enforced via ESLint `import/no-cycle`.
