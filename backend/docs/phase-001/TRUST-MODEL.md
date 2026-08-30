# AGENTPAY — Trust Model

## 1. Multi-Layer Trust Architecture

In AGENTPAY, trust is never treated as a static binary state or a simple static API key assertion. Instead, trust is a dynamic, multi-layered score calculated continuously across five distinct evaluation layers:

$$\text{Total Transaction Trust} = f(\text{Identity}, \text{Policy}, \text{Risk}, \text{Context}, \text{Authorization})$$

```
+-----------------------------------------------------------------------+
|  LAYER 1: IDENTITY TRUST (Is the agent who it claims to be?)          |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  LAYER 2: POLICY COMPLIANCE (Does intent fit user-defined rules?)     |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  LAYER 3: BEHAVIORAL RISK (Is the intent statistically normal?)       |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  LAYER 4: CONTEXTUAL INTEGRITY (Is timing, location, merchant safe?) |
+-----------------------------------------------------------------------+
                                   │
                                   ▼
+-----------------------------------------------------------------------+
|  LAYER 5: AUTHORIZATION STATUS (Does auto-approve or human permit?)   |
+-----------------------------------------------------------------------+
```

---

## 2. Agent Trust Score Formula

Every registered AI AGENT maintains a dynamic **Agent Trust Score** ($T_{\text{agent}}$) normalized between $0$ and $100$:

$$T_{\text{agent}} = w_1 \cdot I_{\text{auth}} + w_2 \cdot O_{\text{ver}} + w_3 \cdot P_{\text{scope}} + w_4 \cdot H_{\text{settle}} + w_5 \cdot B_{\text{consistency}} + w_6 \cdot C_{\text{compliance}} - w_7 \cdot F_{\text{penalties}}$$

### Factor Definitions & Weights

| Factor | Parameter | Weight ($w_i$) | Description |
| :--- | :--- | :--- | :--- |
| **Agent Authentication** | $I_{\text{auth}}$ | 0.15 | Valid cryptographic signature & key pair security level. |
| **Owner Verification** | $O_{\text{ver}}$ | 0.15 | Verification level of human owner (MFA active, KYC completed). |
| **Permission Scope** | $P_{\text{scope}}$ | 0.10 | Specificity of policy rules (tight limits boost trust). |
| **Settlement History** | $H_{\text{settle}}$ | 0.20 | Historical ratio of successfully settled non-flagged transactions. |
| **Behavior Consistency**| $B_{\text{consistency}}$| 0.15 | Deviation score relative to historical spending patterns. |
| **Policy Compliance** | $C_{\text{compliance}}$| 0.15 | Historical record of zero policy violations. |
| **Fraud Penalties** | $F_{\text{penalties}}$ | 0.10 | Deductions for past blocked high-risk attempts or alerts. |

---

## 3. Trust Tiers & Operational Privileges

Based on the computed $T_{\text{agent}}$, AGENTPAY assigns operational trust tiers that determine autonomous spending capabilities:

```
[ 90 - 100 ] : HIGH_TRUST   ──> Eligible for high auto-approval ceiling; streamlined scoring.
[ 70 - 89  ] : MEDIUM_TRUST ──> Standard auto-approval limits; full FraudGuard scoring.
[ 40 - 69  ] : LOW_TRUST    ──> Reduced auto-approval limits; mandatory human review on medium amounts.
[ 00 - 39  ] : UNTRUSTED    ──> Auto-approval disabled; 100% human review / auto-challenge on all intents.
```

---

## 4. Fundamental Trust Guarantees

1. **Identity Alone Is Insufficient**: A valid cryptographic API key proves identity, NOT transaction safety.
2. **Policy Overrides Trust**: Even a `HIGH_TRUST` agent is instantly blocked if it attempts a transaction exceeding explicit spending limits or targeting forbidden categories.
3. **Decay & Recovery**: Trust scores naturally decay slightly during long periods of inactivity and recover incrementally through compliant transaction behavior.
