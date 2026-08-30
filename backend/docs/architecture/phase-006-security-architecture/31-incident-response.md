# AGENTPAY — 31: Incident Response Lifecycle & Containment Playbooks

## 1. Incident Response Lifecycle

```
[ DETECT ] ──> [ CLASSIFY (P0-P3) ] ──> [ CONTAIN ] ──> [ ERADICATE ] ──> [ RECOVER ] ──> [ AUDIT & LESSONS ]
```

---

## 2. Severity Definitions & SLAs

* **P0 (Critical Security Incident)**: Cross-tenant data leak, active payment authorization bypass, compromised master signing secret. *Response SLA*: $< 15\text{ minutes}$.
* **P1 (High Security Incident)**: Suspected agent credential theft, single-user compromise. *Response SLA*: $< 1\text{ hour}$.
