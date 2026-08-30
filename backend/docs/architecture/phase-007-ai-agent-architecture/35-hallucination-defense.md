# AGENTPAY — 35: Verification of LLM Claims Against Authoritative DB Rails

## 1. Authoritative Verification Pipeline

Model-generated statements regarding payment status, prices, merchant identity, or account balances are NEVER trusted.

$$\text{LLM Output: "Payment Succeeded"} \rightarrow \text{Intercept} \rightarrow \text{Query Razorpay Adapter DB Record} \rightarrow \text{Verified Real Status}$$

If the LLM claims a payment succeeded but the relational database record status is `FAILED` or `PENDING`, the backend overrides the text response, informing the user of the real status.
