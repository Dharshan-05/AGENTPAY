# AGENTPAY — 27: Refund Capability Authorization & Policy Checks

## 1. Refund Authorization Controls

* **User Privilege**: Account owners can initiate refunds on fulfilled orders.
* **Agent Privilege**: Agents require explicit `refund:request` capability scope.
* **High-Value Threshold**: Refunds $> ₹10,000$ require step-up MFA or admin approval.
