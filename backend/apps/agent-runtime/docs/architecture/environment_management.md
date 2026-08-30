# AGENTPAY Environment Management Architecture

## Overview & Philosophy

The AGENTPAY backend service (`apps/agent-runtime`) uses an explicit, type-safe environment management strategy. Environment identity is strictly controlled by the `APP_ENV` environment variable, preventing implicit environment inference or silent defaults.

---

## Supported Environments

| Environment (`APP_ENV`) | Description | `DEBUG` Mode Allowed | Intended Runtime Context |
| :--- | :--- | :--- | :--- |
| `local` | Developer workstation | Configurable (`true`/`false`) | Local development |
| `development` | Shared dev environment | Configurable (`true`/`false`) | Non-production dev deployment |
| `test` | Automated test suite | Configurable (`true`/`false`) | CI/CD test runners & Pytest |
| `staging` | Production-like pre-release | Off (`false`) | Pre-production validation |
| `production` | Live customer system | **Forbidden (`false`)** | Production cloud / K8s cluster |

---

## Environment Convenience API

Application code queries environment identity exclusively via `get_settings()`:

```python
from app.core.config import get_settings

settings = get_settings()

if settings.is_production:
    # Production-specific execution path
    pass

if settings.is_local:
    # Local developer convenience path
    pass
```

### Available Properties
- `settings.environment`: Returns `Environment` enum (`local`, `development`, `test`, `staging`, `production`).
- `settings.is_local`: Returns `True` if `APP_ENV=local`.
- `settings.is_development`: Returns `True` if `APP_ENV=development`.
- `settings.is_test`: Returns `True` if `APP_ENV=test`.
- `settings.is_staging`: Returns `True` if `APP_ENV=staging`.
- `settings.is_production`: Returns `True` if `APP_ENV=production`.

---

## Configuration & Environment Precedence

Settings resolution follows a deterministic precedence model:

1. **Process Environment Variables** (Explicit OS / CI / Container runtime `ENV` variables).
2. **Environment File** (`.env`).
3. **Validated Application Defaults** (Pydantic Settings defaults).

---

## Safety & Security Boundaries

1. **Production Safety Policy**: If `APP_ENV=production` and `DEBUG=true`, configuration initialization fails immediately with a `ValueError`, preventing accidental production debug deployments.
2. **Domain Layer Isolation**: Direct access to `os.environ`, `os.getenv`, or `.env` inside `app/domain/` is strictly prohibited by automated architecture tests.
3. **Container & CI/CD Injection**: `.env` files are optional. In containerized (Docker/K8s) or CI environments, configuration is injected entirely through environment variables.
4. **Git Protection**: Secret `.env` files (e.g. `.env`, `.env.local`, `.env.*.local`) are ignored by `.gitignore`. Only `.env.example` is committed.
