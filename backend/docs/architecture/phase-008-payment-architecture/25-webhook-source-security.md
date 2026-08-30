# AGENTPAY — 25: Webhook HMAC-SHA256 Signature Verification Rules

## 1. Signature Verification Algorithm

$$\text{ExpectedSig} = \text{HMAC-SHA256}(\text{RazorpayWebhookSecret}, \text{RawPayloadBody})$$

$$\text{Valid} \iff \text{crypto.timingSafeEqual}(\text{ExpectedSig}, \text{HeaderSig})$$

Unsigned or invalid webhooks fail with HTTP 401 Unauthorized (`ERR_INVALID_WEBHOOK_SIGNATURE`).
