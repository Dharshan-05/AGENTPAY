# AGENTPAY Secrets Configuration Architecture

## Security Overview & Classification

The AGENTPAY backend service (`apps/agent-runtime`) uses a strict, zero-leakage secrets management architecture. Configuration fields are explicitly classified into **Public Configuration** and **Sensitive Secrets**.

```text
                    AGENTPAY
                       │
                 Configuration
                       │
                 ┌─────┴─────┐
                 │           │
             Public       Sensitive
             Config        Secrets
                 │           │
                 ▼           ▼
              Typed       SecretStr
             Settings      + Runtime
                 │           │
                 └─────┬─────┘
                       ▼
                  APPLICATION
                       │
                       ▼
               SECURE RUNTIME
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
         Local        CI/CD       Cloud
        .env*        Secrets     Secret
                                 Manager
```

---

## Secret Classification Matrix

| Setting Parameter | Type Classification | Default Value | Security Handling |
| :--- | :--- | :--- | :--- |
| `APP_NAME`, `APP_VERSION`, `PORT`, `LOG_LEVEL` | Public Configuration | Provided | Plain typed Settings attributes |
| `SECRET_KEY` | Sensitive Secret | `None` | `SecretStr` (Min 32 chars required when set) |
| `DATABASE_URL` | Sensitive Secret | `None` | `SecretStr` (Credential masking) |
| `REDIS_URL` | Sensitive Secret | `None` | `SecretStr` (Credential masking) |
| `JWT_SECRET`, `API_KEY`, `CLIENT_SECRET` | Sensitive Secret | `None` | `SecretStr` (Masked in diagnostics) |

---

## Secret Protections

1. **Automatic String Masking**: All sensitive parameters use `pydantic.SecretStr`. Calling `repr()` or `str()` on settings objects outputs `**********`, preventing accidental print/logging leaks.
2. **Safe Diagnostic Summary (`safe_summary`)**: When operational diagnostic logging is required, settings expose `settings.safe_summary` where sensitive secret attributes are explicitly rendered as `"[REDACTED]"`.
3. **HTTP & OpenAPI Isolation**: Secret fields are never exposed in Pydantic API response models, `/openapi.json`, Swagger docs, or HTTP payloads.
4. **Domain Layer Independence**: Static architecture tests enforce that `app/domain/` Python source files contain zero references to `SecretStr`, `SECRET_KEY`, `DATABASE_URL`, or secret managers.
5. **Git Protection**: Secret environment files (`.env`, `.env.local`, `.env.*.local`) are strictly ignored by `.gitignore`.

---

## Cloud Secret Manager Integration Readiness

The configuration boundary is architected to support future zero-code-change runtime secret injection from cloud secret providers:

- **AWS Secrets Manager / Parameter Store**
- **Azure Key Vault**
- **Google Cloud Secret Manager**
- **HashiCorp Vault**
- **Kubernetes Secrets**

Secrets are injected at process startup via runtime environment variables or container environment injection.
