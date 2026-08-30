# AGENTPAY — 76: Agent Request HMAC-SHA256 Cryptographic Signature Specs

## 1. Request Signature Header Algorithm

$$\text{CanonicalString} = \text{HTTPMethod} \parallel \text{URIPath} \parallel \text{Timestamp} \parallel \text{Nonce} \parallel \text{SHA256}(\text{RequestBody})$$

$$\text{Signature} = \text{HMAC-SHA256}(\text{AgentSecretKey}, \text{CanonicalString})$$

Submitted via header: `X-Agent-Signature: t=1771960000,n=nonce_123,v1=sig_hash`.
