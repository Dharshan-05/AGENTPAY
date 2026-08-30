# AGENTPAY — Agent Lifecycle & Identity

## 1. Lifecycle State Machine

Every AI AGENT registered within AGENTPAY moves through a strictly governed state machine. State transitions dictate whether an agent can authenticate, submit payment intents, or query system status.

```
       +--------------------+
       |     REGISTERED     | (Credentials issued, policies unconfigured)
       +--------------------+
                 │
                 ▼ (Policy set & verified by Owner)
       +--------------------+
       |       ACTIVE       | <=======> +--------------------+
       +--------------------+           |       PAUSED       | (Owner manually paused)
                 │                      +--------------------+
                 ├─── (Security anomaly / High risk policy violation) ──┐
                 │                                                      ▼
                 ├─── (Owner Emergency Stop triggered) ────────> +--------------------+
                 │                                              |     SUSPENDED      |
                 │                                              +--------------------+
                 ▼ (Owner hard revocation)                                │
       +--------------------+                                            │
       |      REVOKED       | <──────────────────────────────────────────┘
       +--------------------+ (Terminal State: Credentials permanently invalidated)
```

---

## 2. Lifecycle State Definitions

| State | Intent Creation | Status Query | Description |
| :--- | :--- | :--- | :--- |
| **REGISTERED** | Disabled | Enabled | Agent record created, API keys issued, awaiting owner policy initial setup. |
| **ACTIVE** | Enabled | Enabled | Agent fully authorized to submit payment intents subject to AGENTGUARD policy checks. |
| **PAUSED** | Disabled | Enabled | Temporarily deactivated by owner (e.g. agent maintenance window). |
| **SUSPENDED** | Disabled | Enabled | Automatically halted by system due to security alerts or Emergency Stop switch. |
| **REVOKED** | Disabled | Disabled | Permanently invalidated identity. All future requests fail authentication immediately. |

---

## 3. Cryptographic Credential Management

### 3.1 Key Generation & Storage
1. Upon registration, AGENTPAY issues an `Agent ID` (UUID v4) and a 256-bit cryptographically secure HMAC API Key (`secret_key`).
2. The `secret_key` is displayed to the user **once** upon creation and stored in hashed form (using Argon2id / bcrypt) inside the database.
3. For enterprise integrations, RSA/Ed25519 public key pairs are supported, where the AI AGENT signs requests with its private key and AGENTPAY verifies against the registered public key.

### 3.2 Key Rotation & Revocation Protocols
* **Scheduled Rotation**: Users can initiate key rotation from the dashboard, generating a secondary key with a 24-hour grace overlap period.
* **Instant Revocation**: Executing a revocation API call or clicking "Revoke Agent" immediately purges active key hashes from the Redis edge authentication cache, stopping agent requests at the gateway within < 10ms.

---

## 4. Request Authentication Protocol

Every incoming request from an AI AGENT to AGENTPAY must include cryptographic authorization headers:

```http
POST /api/v1/payment-intents HTTP/1.1
Host: api.agentpay.io
X-Agent-ID: agt_98a12c44
X-Agent-Timestamp: 1724509319
X-Agent-Nonce: n_8f12a4b
X-Agent-Signature: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### Signature Construction
```text
Signature = HMAC-SHA256(
    Key = agent_secret_key,
    Data = Agent-ID + ":" + Timestamp + ":" + Nonce + ":" + HTTP_Method + ":" + Request_Path + ":" + SHA256(Request_Body)
)
```

This protocol guarantees:
* **Authenticity**: Verifies the request originates from the specified AI AGENT.
* **Integrity**: Prevents payload tampering in transit.
* **Replay Protection**: Rejecting requests where `Timestamp` is older than 300 seconds or where `Nonce` has been seen within the replay window.
