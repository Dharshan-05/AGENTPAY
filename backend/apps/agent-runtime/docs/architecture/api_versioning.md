# AGENTPAY API Versioning Architecture

## Overview & Strategy

The AGENTPAY backend service (`apps/agent-runtime`) uses explicit **URL Path Versioning** (`/api/v1/...`). API versioning provides a clean, predictable, and backward-compatible contract boundary for public API consumers before feature endpoints are implemented.

```text
                             FastAPI Application
                                (app/main.py)
                                      │
                                      ▼
                               Root API Router
                             (app/api/router.py)
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                  GET / (Root)            v1 API Router
                 (System status)       (app/api/v1/router.py)
                                           [prefix: /api/v1]
                                                   │
                                     ┌─────────────┼─────────────┐
                                     ▼             ▼             ▼
                                   Auth          Agents       Payments
                                (v1 feature)   (v1 feature)  (v1 feature)
```

---

## Canonical Prefix Configuration (`app/core/config.py`)

Prefixes are derived dynamically from environment configuration settings:
- `API_PREFIX`: `"/api"`
- `API_V1_PREFIX`: `"/v1"`
- `api_v1_str`: `f"{api_prefix}{api_v1_prefix}"` → `"/api/v1"`

Hard-coding string literals like `"/api/v1"` inside feature controllers or application modules is strictly prohibited.

---

## Key Architectural Rules & Layer Isolation

1. **API Layer Ownership**: Versioning belongs strictly to `app/api/`. Domain (`app/domain/`), application (`app/application/`), and infrastructure (`app/infrastructure/`) layers MUST retain ZERO awareness of version numbers, router prefixes, `FastAPI`, or HTTP request objects.
2. **Unknown Version Safety**: Unmapped API versions (e.g. `/api/v2/foo`, `/api/v999/bar`) fail safely with HTTP `404 Not Found`. Fallbacks mapping unknown versions to `v1` are prohibited.
3. **No Duplicate Prefixes**: Router mounting composition prevents duplicate prefix errors (`/api/api/v1` or `/api/v1/api/v1`).
4. **No Version Aliases**: Public contracts use explicit version prefixes (`/api/v1`). Ambiguous aliases like `/api/latest` or `/api/current` are prohibited.
5. **No Fake Business APIs**: Feature routers are mounted as explicit extension points (`auth`, `users`, `agents`, `payments`, `transactions`) without creating fake production routes.

---

## Future Versioning & Lifecycle Strategy

- **Active State**: `/api/v1` is the current active, stable public contract.
- **Future v2 Extension**: A future `v2` will be created under `app/api/v2/router.py` and mounted in `app/api/router.py` under prefix `get_settings().api_v2_str` (`"/api/v2"`).
- **Deprecation Lifecycle**:
  1. `ACTIVE`: Fully supported public API.
  2. `DEPRECATED`: Sunset timeline announced; response headers advertise deprecation schedule.
  3. `SUNSET`: Route unmounted; returns `410 Gone` or `404 Not Found`.

---

## Future Phase Integration

- **Phase 020 (Current)**: URL Path Versioning Architecture (`/api/v1`), router composition, configuration prefix derivation, unknown version 404 safety, layer isolation, and OpenAPI compatibility.
- **Phase 021**: API Middleware.
- **Phase 028**: API Documentation.
- **Phase 029**: OpenAPI Advanced Configuration.
