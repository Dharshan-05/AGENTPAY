# AGENTPAY — 02: PNPM Workspace Monorepo Strategy & Package Resolution

## 1. Selected Monorepo Tooling

* **Workspace Protocol**: PNPM Workspaces (`pnpm-workspace.yaml`).
* **Dependency Protocol**: Internal workspace packages reference `@agentpay/<pkg>` via `"workspace:*"`.
* **Task Orchestration**: Turborepo / PNPM filtering (`pnpm --filter ...`) for incremental caching and parallel builds.
* **Platform Support**: Native Windows (pwsh/cmd) and Linux CI runner compatibility.
