# AGENTPAY — 47: Verified Payment Status User Notifications

## 1. Notification Rules

Payment notifications (Push, Email, In-App) are generated exclusively upon receiving authoritative settlement signals (`PaymentSucceeded` or `PaymentFailed`). Notifications are NEVER generated from LLM text responses.
