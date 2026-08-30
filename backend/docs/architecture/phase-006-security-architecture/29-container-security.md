# AGENTPAY — 29: Docker Non-Root Container Security & Read-Only Root

## 1. Container Hardening Rules

1. **Non-Root Execution**: Docker containers run under dedicated unprivileged system users (`USER node` / `USER app`). Running as `root` is forbidden.
2. **Minimal Base Images**: Distroless or Alpine Linux minimal base images to minimize attack surface.
3. **Read-Only Root Filesystem**: Container root filesystem mounted as read-only (`read_only: true`). Temporary writes restricted to `/tmp` volume.
4. **Dropped Capabilities**: Drop all Linux capabilities (`cap_drop: - ALL`), adding back only required bindings (`cap_add: - NET_BIND_SERVICE`).
