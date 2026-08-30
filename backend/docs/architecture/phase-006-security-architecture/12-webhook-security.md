# AGENTPAY — 12: Webhook HMAC Verification & Replay Protection

## 1. Webhook Security Architecture

All incoming webhooks from Razorpay or external merchants undergo mandatory security validation prior to processing.

```
[ Incoming Webhook ]
        │
        ▼
[ 1. Verify X-Razorpay-Signature HMAC Header ] ──(Invalid)──> REJECT (401)
        │
        ▼
[ 2. Verify IP Whitelist / ASN ] ────────────────(Invalid)──> REJECT (403)
        │
        ▼
[ 3. Idempotency Check (Razorpay Event ID) ] ────(Duplicate)─> HTTP 200 OK (Cached)
        │
        ▼
[ 4. State Machine Transition Verification ] ────(Invalid)──> REJECT (422)
        │
        ▼
[ 5. Process & Append SHA-256 Audit Entry ]
```

---

## 2. HMAC Signature Verification

$$\text{Signature} = \text{HMAC-SHA256}(\text{RazorpayWebhookSecret}, \text{RawRequestBody})$$

Constant-time string comparison (`crypto.timingSafeEqual`) prevents timing attacks.
