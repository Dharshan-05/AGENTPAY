# AGENTPAY — 02: 15 Non-Negotiable Zero-Trust Security Principles

## 1. Core Principles Blueprint

```
+-----------------------------------------------------------------------+
|                    15 ZERO-TRUST SECURITY PRINCIPLES                  |
+-----------------------------------------------------------------------+
|  1. Zero Trust Architecture (Never Trust, Always Verify)             |
|  2. Least Privilege (Scoped Capability Delegation)                    |
|  3. Defense in Depth (Multi-Layered Security Control Plane)          |
|  4. Secure by Default (Default Deny / Unconfigured Ceiling = Zero)     |
|  5. Fail Closed (System Faults Default to BLOCK or REVIEW)            |
|  6. Explicit Authorization (Authentication != Financial Permission)   |
|  7. Strong Identity (Cryptographic Binding of Agent to Human Owner)   |
|  8. Continuous Verification (Per-Request Policy & Risk Checks)        |
|  9. Separation of Duties (Agent Planner Isolated from AgentGuard)     |
| 10. Assume Breach (Containment via Network & Tenant Isolation)       |
| 11. Data Minimization (Zero Raw Banking Secrets in LLM Contexts)      |
| 12. Immutable Auditability (Tamper-Evident Block Hashing Chain)       |
| 13. Secure Supply Chain (SBOM, SAST/DAST, Signed Containers)          |
| 14. Human Oversight Supremacy (Human Escalations & Kill Switch)       |
| 15. Payment Safety First (Idempotency & Replay Protection over Speed) |
+-----------------------------------------------------------------------+
```

---

## 2. Enforcement Standards

* **Principle 5 (Fail Closed)**: If the ML container or database times out, AGENTGUARD defaults to `BLOCK` or `REVIEW`. Systems NEVER default to `ALLOW`.
* **Principle 9 (Separation of Duties)**: Agent logic runs in Zone 3 (Agent Execution); AGENTGUARD runs in Zone 4 (Security Control Plane). Agents cannot alter their own policy rules.
