# AGENTPAY — Requirement Traceability Matrix

## 1. Traceability Model Structure

The AGENTPAY Traceability Matrix ensures 100% bidirectional alignment from original core problems down to test suite acceptance criteria:

$$\text{Problem Domain} \longrightarrow \text{Stakeholder Requirement} \longrightarrow \text{System Requirement} \longrightarrow \text{Acceptance Criteria} \longrightarrow \text{Test Suite}$$

---

## 2. Traceability Matrix Table

| Problem Domain | Stakeholder Req | System Requirement | Acceptance Criteria | Test Suite |
| :--- | :--- | :--- | :--- | :--- |
| **Agent Identity** | `STK-AGT-01` | `REQ-AUTH-002` (HMAC Signature) | `AC-AUTH-002` | `test_agent_hmac_auth()` |
| **Agent Identity** | `STK-USR-01` | `REQ-AGENT-001` (Enrolment) | `AC-AGENT-001` | `test_agent_registration()` |
| **Replay / Spoofing** | `STK-AGT-01` | `REQ-AUTH-003` (Timestamp Window)| `AC-AUTH-003` | `test_timestamp_expiration()`|
| **Replay / Spoofing** | `STK-AGT-01` | `REQ-AUTH-004` (Nonce Cache) | `AC-AUTH-004` | `test_nonce_replay_block()` |
| **Autonomous Spending**| `STK-USR-02` | `REQ-POLICY-001` (Single Limit) | `AC-POLICY-001` | `test_single_limit_exceeded()`|
| **Category Risk** | `STK-USR-02` | `REQ-POLICY-002` (Category Block) | `AC-POLICY-002` | `test_category_blocked()` |
| **Autonomy Balance** | `STK-USR-02` | `REQ-POLICY-003` (Auto Ceiling) | `AC-POLICY-003` | `test_auto_approval_threshold()`|
| **Runaway Agent** | `STK-USR-04` | `REQ-POLICY-004` (Emergency Stop)| `AC-POLICY-004` | `test_emergency_stop_kill()` |
| **Double Spending** | `STK-AGT-03` | `REQ-PAY-002` (Idempotency) | `AC-PAY-002` | `test_idempotent_duplicate()` |
| **Fraud Detection** | `STK-ANL-01` | `REQ-FRAUD-001` (Features) | `AC-FRAUD-001` | `test_feature_extraction()` |
| **Fraud Scoring** | `STK-ANL-01` | `REQ-FRAUD-002` (Risk Score) | `AC-FRAUD-001` | `test_risk_scoring_matrix()` |
| **Black-Box AI** | `STK-USR-05` | `REQ-XAI-001` (Feature Importance)| `AC-XAI-001` | `test_xai_feature_attribution()`|
| **Black-Box AI** | `STK-USR-05` | `REQ-XAI-002` (Text Explanation) | `AC-XAI-001` | `test_xai_natural_text()` |
| **Human Control** | `STK-USR-03` | `REQ-APP-001` (Real-Time Alert) | `AC-APP-001` | `test_approval_escalation()` |
| **Human Control** | `STK-USR-03` | `REQ-APP-002` (Human Action) | `AC-APP-001` | `test_user_approval_execution()`|
| **Auditability** | `STK-ANL-02` | `REQ-AUD-001` (Immutable Log) | `AC-AUD-001` | `test_immutable_audit_log()` |
