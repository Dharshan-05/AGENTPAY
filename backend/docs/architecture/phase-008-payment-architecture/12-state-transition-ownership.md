# AGENTPAY — 12: State Transition Authority & Execution Rights Matrix

## 1. Transition Authority Matrix

| Target State Transition | Authorized Component Owner | Required Precondition / Trigger |
| :--- | :--- | :--- |
| `CREATED` $\rightarrow$ `VALIDATING` | API Gateway Edge | Schema validation pass |
| `VALIDATING` $\rightarrow$ `RISK_CHECK` | AGENTGUARD Policy Engine | Single limit & category rule pass |
| `RISK_CHECK` $\rightarrow$ `AUTHORIZED` | AGENTGUARD / Approval Center | Risk score pass / Human click "APPROVE" |
| `AUTHORIZED` $\rightarrow$ `PAYMENT_INITIATED`| Payment Orchestrator | Valid `PaymentAuthorizationContext` signature |
| `PROCESSING` $\rightarrow$ `SUCCESS` | Razorpay Adapter / Webhook Listener| Razorpay settlement confirmation payload |
| `PROCESSING` $\rightarrow$ `PAYMENT_STATUS_UNKNOWN`| Payment Orchestrator | 5,000ms Gateway Provider Timeout |
| `UNKNOWN` $\rightarrow$ `SUCCESS` / `FAILED` | Reconciliation Worker Service | Direct Razorpay GET API status verification |

Client web frontends and AI agents possess ZERO authority to trigger state machine transitions directly.
