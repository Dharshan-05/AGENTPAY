# AGENTPAY — Authentication Functional Specifications

## 1. Overview

This document specifies the exact observable functional behavior for user and AI AGENT authentication mechanisms in AGENTPAY.

---

## 2. Specifications

### FR-AUTH-001: User Registration & Account Setup
* **FR ID**: `FR-AUTH-001`
* **Title**: User Account Registration & Profile Setup
* **Source**: `REQ-AUTH-001`, `REQ-USR-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`)
* **Goal**: Register a new human account owner and initialize MFA credentials.
* **Preconditions**: User is on the public registration portal; email is unregistered.
* **Trigger**: User submits email, password, and full name.
* **Inputs**: `email` (string), `password` (string), `full_name` (string).
* **Main Flow**:
  1. User enters registration details and submits form.
  2. System validates email format and password strength (min 12 chars, mixed case, numbers, symbols).
  3. System hashes password using Argon2id ($m=65536, t=3, p=4$).
  4. System generates secret TOTP seed and displays QR code to user.
  5. User scans QR code into authenticator app and enters 6-digit verification code.
  6. System verifies code against TOTP seed.
  7. System sets user status to `ACTIVE` and issues initial JWT session token.
* **Alternative Flows**:
  * *AF-1 (Duplicate Email)*: If email exists, return `ERR_EMAIL_EXISTS`.
  * *AF-2 (Invalid MFA Code)*: If TOTP verification fails, prompt user to re-enter code.
* **Business Rules**: `BR-001`, `BR-002`.
* **Validation Rules**: Email must conform to RFC 5322; password length $\ge 12$.
* **Authorization Rules**: Public endpoint; rate limited to 5 attempts/minute per IP.
* **State Changes**: User record created in `ACTIVE` state; session created.
* **Outputs**: JWT access token (15m TTL), refresh token (7d TTL), user profile object.
* **Error Conditions**: `ERR_INVALID_EMAIL`, `ERR_WEAK_PASSWORD`, `ERR_MFA_FAILED`.
* **Security Requirements**: TLS 1.3 mandated; password stored in Argon2id hash only.
* **Audit Events**: `EVENT_USER_REGISTERED`, `EVENT_MFA_ENROLLED`.
* **Acceptance Criteria**: `AC-AUTH-001`.
* **Dependencies**: None.

---

### FR-AUTH-002: User MFA Password Login
* **FR ID**: `FR-AUTH-002`
* **Title**: User MFA Password & Session Authentication
* **Source**: `REQ-AUTH-001`
* **Priority**: P0 | **MVP**: YES
* **Actor**: Human User Account Owner (`USER`)
* **Goal**: Authenticate human user credentials and establish a secure session.
* **Preconditions**: User account exists in `ACTIVE` state.
* **Trigger**: User submits login form with email, password, and TOTP code.
* **Inputs**: `email` (string), `password` (string), `totp_code` (string).
* **Main Flow**:
  1. User submits login credentials and 6-digit MFA code.
  2. System fetches user record by email.
  3. System verifies password hash using Argon2id.
  4. System verifies 6-digit code against TOTP seed.
  5. System generates signed JWT access token and HTTP-only refresh cookie.
  6. System updates last login timestamp and resets failed login counters.
* **Alternative Flows**:
  * *AF-1 (Failed Credentials)*: Increment failed login counter; return `ERR_INVALID_CREDENTIALS`.
  * *AF-2 (Account Locked)*: If failed attempts $\ge 5$, lock account for 15 minutes (`ERR_ACCOUNT_LOCKED`).
* **Business Rules**: `BR-001`.
* **Validation Rules**: TOTP code must be 6 digits within current time window.
* **Authorization Rules**: Public login endpoint; rate limited to 10 attempts/minute per IP.
* **State Changes**: Session token created; failed attempt counters updated.
* **Outputs**: JWT token string, user profile JSON.
* **Error Conditions**: `ERR_INVALID_CREDENTIALS`, `ERR_ACCOUNT_LOCKED`, `ERR_MFA_INVALID`.
* **Security Requirements**: No password details exposed in error responses.
* **Audit Events**: `EVENT_USER_LOGIN_SUCCESS`, `EVENT_USER_LOGIN_FAILED`.
* **Acceptance Criteria**: `AC-AUTH-001`.
* **Dependencies**: `FR-AUTH-001`.

---

### FR-AUTH-003: Agent HMAC Request Signature Verification
* **FR ID**: `FR-AUTH-003`
* **Title**: AI Agent HMAC Cryptographic Request Authentication
* **Source**: `REQ-AUTH-002`
* **Priority**: P0 | **MVP**: YES
* **Actor**: AI AGENT (`AI AGENT`)
* **Goal**: Authenticate incoming API requests from autonomous agents.
* **Preconditions**: Agent is registered and has assigned `Agent ID` and `secret_key`.
* **Trigger**: AI Agent submits HTTP request to Agent Gateway API endpoints.
* **Inputs**: HTTP Headers (`X-Agent-ID`, `X-Agent-Timestamp`, `X-Agent-Nonce`, `X-Agent-Signature`), Request Body.
* **Main Flow**:
  1. Gateway extracts authentication headers from incoming request.
  2. Gateway looks up agent record and secret key hash in Redis edge cache.
  3. Gateway constructs canonical request string: `AgentID:Timestamp:Nonce:Method:Path:SHA256(Body)`.
  4. Gateway computes expected HMAC-SHA256 signature using agent's `secret_key`.
  5. Gateway performs constant-time string comparison between computed signature and `X-Agent-Signature`.
  6. If signatures match, request is marked `AUTHENTICATED` and passed to pipeline.
* **Alternative Flows**:
  * *AF-1 (Missing Headers)*: Return HTTP 401 `ERR_MISSING_AUTH_HEADERS`.
  * *AF-2 (Signature Mismatch)*: Return HTTP 401 `ERR_INVALID_SIGNATURE`.
  * *AF-3 (Agent Revoked)*: Return HTTP 403 `ERR_AGENT_REVOKED`.
* **Business Rules**: `BR-001`, `BR-002`.
* **Validation Rules**: Headers must be non-null; signature comparison must use constant-time execution (`crypto.timingSafeEqual`).
* **Authorization Rules**: Validates identity only; does NOT authorize payment.
* **State Changes**: None (stateless authentication check).
* **Outputs**: Authenticated Agent Context attached to request state.
* **Error Conditions**: `ERR_MISSING_AUTH_HEADERS`, `ERR_INVALID_SIGNATURE`, `ERR_AGENT_NOT_FOUND`.
* **Security Requirements**: Constant-time signature comparison to prevent timing attacks.
* **Audit Events**: `EVENT_AGENT_AUTH_SUCCESS`, `EVENT_AGENT_AUTH_FAILED`.
* **Acceptance Criteria**: `AC-AUTH-002`.
* **Dependencies**: `FR-AGENT-001`.

---

### FR-AUTH-004: Request Timestamp Expiration Validation
* **FR ID**: `FR-AUTH-004`
* **Title**: Request Timestamp Expiration Window Validation
* **Source**: `REQ-AUTH-003`
* **Priority**: P0 | **MVP**: YES
* **Actor**: AI AGENT (`AI AGENT`)
* **Goal**: Prevent stale or delayed request execution by enforcing a strict timestamp window.
* **Preconditions**: Agent API request contains `X-Agent-Timestamp` header.
* **Trigger**: Ingestion of agent HTTP request header parsing phase.
* **Inputs**: `X-Agent-Timestamp` (UNIX epoch integer seconds).
* **Main Flow**:
  1. System reads current server time ($T_{\text{server}}$).
  2. System parses request timestamp ($T_{\text{req}}$).
  3. System calculates absolute time delta: $\Delta T = |T_{\text{server}} - T_{\text{req}}|$.
  4. If $\Delta T \le 300\text{ seconds}$ (5 minutes), validation passes.
* **Alternative Flows**:
  * *AF-1 (Timestamp Expired)*: If $\Delta T > 300\text{ seconds}$, terminate request immediately and return HTTP 401 `ERR_TIMESTAMP_EXPIRED`.
* **Business Rules**: `BR-001`.
* **Validation Rules**: $T_{\text{req}}$ must be valid 10-digit epoch integer.
* **Authorization Rules**: Pre-authorization validation step.
* **State Changes**: None.
* **Outputs**: Timestamp Validation Pass/Fail signal.
* **Error Conditions**: `ERR_TIMESTAMP_EXPIRED`, `ERR_INVALID_TIMESTAMP_FORMAT`.
* **Security Requirements**: Protects against stale request execution and clock skew exploits.
* **Audit Events**: `EVENT_TIMESTAMP_EXPIRED_REJECTION`.
* **Acceptance Criteria**: `AC-AUTH-003`.
* **Dependencies**: `FR-AUTH-003`.

---

### FR-AUTH-005: Replay Nonce Cache Validation
* **FR ID**: `FR-AUTH-005`
* **Title**: Replay Protection via Redis Nonce Cache
* **Source**: `REQ-AUTH-004`
* **Priority**: P0 | **MVP**: YES
* **Actor**: AI AGENT (`AI AGENT`)
* **Goal**: Prevent replay attacks of identical signed API requests.
* **Preconditions**: Request passes signature and timestamp validation.
* **Trigger**: Ingestion of `X-Agent-Nonce` header.
* **Inputs**: `X-Agent-ID` (string), `X-Agent-Nonce` (string UUID v4).
* **Main Flow**:
  1. System constructs Redis cache key: `nonce:<agent_id>:<nonce_string>`.
  2. System executes atomic Redis `SETNX` (Set if Not Exists) command with 900s (15m) TTL.
  3. If key was successfully written (returns 1), nonce is unique and validation passes.
* **Alternative Flows**:
  * *AF-1 (Duplicate Nonce)*: If key already exists (returns 0), terminate request immediately and return HTTP 401 `ERR_REPLAY_ATTEMPT`.
* **Business Rules**: `BR-001`.
* **Validation Rules**: Nonce must be valid string $\ge 16$ chars.
* **Authorization Rules**: Pre-authorization validation step.
* **State Changes**: Nonce string cached in Redis with 15-minute TTL.
* **Outputs**: Nonce Validation Pass/Fail signal.
* **Error Conditions**: `ERR_REPLAY_ATTEMPT`.
* **Security Requirements**: Guarantees zero request replay within 15-minute window.
* **Audit Events**: `EVENT_REPLAY_ATTACK_BLOCKED`.
* **Acceptance Criteria**: `AC-AUTH-004`.
* **Dependencies**: `FR-AUTH-003`.
