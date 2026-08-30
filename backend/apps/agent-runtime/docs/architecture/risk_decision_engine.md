# RISK & DECISION ENGINE Architecture Specification — Groups 1–13 (Phases 266–292)

## Overview
Groups 1–13 (Phases 266–292) establish the complete, centralized, deterministic, tenant-isolated, agent-isolated, and point-in-time safe **Risk & Decision Engine** architecture, **Risk Signal Normalization** layer, **Upstream Source Risk Integrations** (AGENTGUARD, FraudGuard, Behaviour Risk, Intent Risk, and Policy Risk), **Risk Fusion Engine**, **Risk Weight Configuration**, **Composite Advisory Risk Score Calculation**, **Risk Threshold Configuration & Classification**, **Hard Security Rules Engine**, **Final Authoritative Risk Decision Engine** (ALLOW, REVIEW, BLOCK), **Decision Governance, Explanation, Audit, Replay & Enforcement Gate**, **Risk Decision REST API & Audit Subsystem**, **Payment Authorization Gate**, **Razorpay Integration Setup**, **Razorpay Credentials Storage**, **Payment Application Service Boundary**, **Razorpay Payment Order Creation (Phase 289)**, **Razorpay Checkout Integration (Phase 290)**, **Payment Verification Subsystem (Phase 291)**, and **Authoritative Payment Status State Machine (Phase 292)** for AGENTPAY (`apps/agent-runtime`).

```text
                                AUTHORITATIVE RISK SOURCES
        ┌───────────────────┬───────────────────┬───────────────────┬───────────────────┐
        │                   │                   │                   │                   │
   AGENTGUARD           FRAUDGUARD          BEHAVIOUR            INTENT              POLICY
 (AgentRiskProfile,   (FraudProbability,  (BehaviourRiskResult,(IntentRiskResult,   (PolicyRiskResult,
  BehaviourRisk)       TransactionRisk)   MLBehaviourRisk)     IntentConfidence)    PolicyDecision)
        │                   │                   │                   │                   │
        ▼                   ▼                   ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  PHASE 268    │   │  PHASE 269    │   │  PHASE 270    │   │  PHASE 271    │   │  PHASE 272    │
│ AGENTGUARD    │   │ FRAUDGUARD    │   │ BEHAVIOUR     │   │ INTENT        │   │ POLICY        │
│ SERVICE       │   │ SERVICE       │   │ SERVICE       │   │ SERVICE       │   │ SERVICE       │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │                   │                   │
        └───────────────────┴─────────┬─────────┴───────────────────┴───────────────────┘
                                      │
                                      ▼
                         CANONICAL RiskSignal OBJECTS
                                      │
                                      ▼
                           ┌────────────────────┐
                           │   PHASE 267        │
                           │ SIGNAL NORMALIZER  │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │   PHASE 273        │
                           │ RISK FUSION ENGINE │
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │   PHASE 275        │
                           │ RISK WEIGHT SERVICE│
                           └─────────┬──────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │   PHASE 274        │
                           │ SCORE CALCULATOR   │
                           └─────────┬──────────┘
                                     │
                                     ▼
                     COMPOSITE ADVISORY RISK SCORE [0,100]
                                     │
                        ┌────────────┴────────────┐
                        │                         │
                        ▼                         ▼
            ┌──────────────────────┐  ┌──────────────────────┐
            │   PHASE 276          │  │   PHASE 277          │
            │ THRESHOLD EVALUATION │  │ HARD SECURITY RULES  │
            └───────────┬──────────┘  └───────────┬──────────┘
                        │                         │
                        └────────────┬────────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │  PHASES 278-280    │
                           │   FINAL DECISION   │
                           │       ENGINE       │
                           └─────────┬──────────┘
                                     │
                         ┌───────────┼───────────┐
                         ▼           ▼           ▼
                       ALLOW       REVIEW      BLOCK
                         │           │           │
             ┌───────────┴───────────┼───────────┴───────────┐
             │                       │                       │
             ▼                       ▼                       ▼
   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
   │    PHASE 282     │    │    PHASE 283     │    │    PHASE 284     │
   │   EXPLANATION    │    │   DECISION AUDIT │    │   RISK DECISION │
   │      ENGINE      │    │      ENGINE      │    │     REST API     │
   └─────────┬────────┘    └─────────┬────────┘    └─────────┬────────┘
             │                       │                       │
             └───────────────────────┼───────────────────────┘
                                     │
                                     ▼
                           ┌────────────────────┐
                           │     PHASE 285      │
                           │      PAYMENT       │
                           │ AUTHORIZATION GATE │
                           └─────────┬──────────┘
                                     │
                         ┌───────────┼───────────┐
                         ▼           ▼           ▼
                     PERMITTED   SUSPENDED    DENIED
                         │           │           │
                         ▼           ▼           ▼
                 ┌───────────────┐ ┌── STOP  ┌── STOP
                 │   PHASE 288   │
                 │    PAYMENT    │
                 │    SERVICE    │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   PHASE 289   │
                 │ RAZORPAY ORDER│
                 │   CREATION    │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   PHASE 290   │
                 │    CHECKOUT   │
                 │ CONFIGURATION │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   PHASE 291   │
                 │    PAYMENT    │
                 │ VERIFICATION  │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                  │   PHASE 292   │
                  │ PAYMENT STATUS│
                  │ STATE MACHINE │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   PHASE 293   │
                  │WEBHOOK HANDLER│
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   PHASE 294   │
                  │   SIGNATURE   │
                  │ VERIFICATION  │
                  └─────────┬───────┘
                            │
                            ▼
               VERIFIED WEBHOOK ENVELOPE
                           │
                           ▼
                   ┌───────────────┐
                   │   PHASE 295   │
                   │ PAYMENT EVENT │
                   │  PROCESSING   │
                   └─────────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │   PHASE 296   │
                   │PAYMENT FAILURE│
                   │   HANDLING    │
                   └─────────┬───────┘
                           │
                           ▼
                   ┌───────────────┐
                   │   PHASE 297   │
                   │    PAYMENT    │
                   │  IDEMPOTENCY  │
                   └───────────────┘
```

## Group 14: Phases 293–294 Webhook Ingestion & Signature Verification Boundary

- **Phase 293 — Webhook Handler (`RazorpayWebhookHandler`)**:
  - Ingests raw Razorpay HTTP request bytes via `POST /api/v1/payments/webhooks/razorpay`.
  - Invokes Phase 294 signature verification BEFORE any JSON parsing or event object creation.
  - Replay Defense: Detects duplicate event IDs / payload fingerprints using `WebhookReplayTracker`.
  - Constructs `VerifiedWebhookEnvelope` ONLY after signature verification passes.

- **Phase 294 — Webhook Signature Verification (`RazorpayWebhookSignatureVerifier`)**:
  - Operates on exact raw HTTP request body bytes (`bytes`), NOT parsed JSON.
  - Computes `HMAC-SHA256(raw_body, webhook_secret)` and performs timing-safe comparison using `hmac.compare_digest()`.
  - Resolves webhook secret via `RazorpayCredentialResolver` (with tenant and environment isolation).
  - Keeps secrets (`webhook_secret`, `key_secret`) strictly hidden (0 secret exposure in result models, exception strings, or logs).

## Group 15: Phases 296–297 Payment Failure Handling & Payment Idempotency

- **Phase 296 — Payment Failure Handling (`PaymentFailureService`)**:
  - Centralized, deterministic, security-safe payment failure normalization.
  - Strongly typed failure taxonomy (`PaymentFailureCategory`, `PaymentFailureCode`, `PaymentFailureRecord`).
  - Strict Guarantee: A failure event can NEVER produce `payment_success=True`, `payment_verified=True`, or `captured=True`.
  - Sanitizes error messages to strip all credentials, `key_secret`, `webhook_secret`, Bearer tokens, or JWTs.
  - Integrates with `PaymentStatusService` to execute status transitions to `FAILED` without violating state machine matrix boundaries.
  - Generates deterministic SHA-256 `failure_fingerprint` over safe metadata.

- **Phase 297 — Payment Idempotency (`PaymentIdempotencyService`)**:
  - Authoritative multi-tenant payment idempotency subsystem executing BEFORE external financial side effects (`PaymentService.create_payment_order()`).
  - Identity Binding: Bound to `tenant_id` + `agent_id` + `transaction_id` + `operation` + `idempotency_key`.
  - Request Fingerprinting: Calculates SHA-256 fingerprint over canonical request parameters. Rejects modified requests with same key (`IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_REQUEST`, 409 Conflict).
  - Lifecycle States: `IN_PROGRESS`, `COMPLETED`, `FAILED`. Thread-safe concurrency reservation prevents duplicate external calls.

## Group 16: Phases 298–299 Payment Lifecycle Control (Cancellation & Refund)

- **Phase 298 — Payment Cancellation Flow (`PaymentCancellationService`)**:
  - Server-side order cancellation service governed by existing state machine, authorization, and provider abstraction layers.
  - Allowed Cancellation Eligibility: `CREATED`, `ORDER_CREATED`, `CHECKOUT_READY`, `PAYMENT_PENDING` -> `CANCELLED`.
  - Rejected Eligibility: `PAYMENT_RECEIVED`, `PAYMENT_VERIFIED`, `CAPTURED`, `REFUNDED`, `FAILED`, `CANCELLED`.
  - Strict Terminal Guard: `CAPTURED` payments can NEVER be cancelled (cancellation is NOT refund).
  - Multi-Tenant Idempotency: Integrates with `PaymentIdempotencyService` (`operation = "payment_cancellation"`).
  - Failure Integration: Routes provider errors through `PaymentFailureService`.

- **Phase 299 — Payment Refund Flow (`PaymentRefundService`)**:
  - Server-side payment refund service for captured payments.
  - Allowed Refund Eligibility: `CAPTURED` -> `REFUNDED` ONLY.
  - Rejected Eligibility: `CREATED`, `ORDER_CREATED`, `CHECKOUT_READY`, `PAYMENT_PENDING`, `PAYMENT_RECEIVED`, `PAYMENT_VERIFIED`, `FAILED`, `CANCELLED`, `REFUNDED`.
  - Decimal Monetary Precision: Supports full/partial refunds using strict `Decimal` monetary calculations (`refund_amount > 0`, `refund_amount <= captured_amount`). Rejects NaN, Infinity, negative values, and excessive decimal places (>2).
  - Multi-Tenant Idempotency: Integrates with `PaymentIdempotencyService` (`operation = "payment_refund"`). Request fingerprint contains payment ID, order ID, refund amount, currency, and provider name.

## Group 17: Phases 300–301 Secure Agent Boundary & Approval Architecture

- **Phase 300 — Secure Agent-to-Razorpay Boundary (`AgentPaymentBoundary`)**:
  - Dedicated server-side boundary strengthening isolation between autonomous agents and Razorpay provider layer.
  - Agent is a REQUESTER ONLY, never a payment authority.
  - Zero agent access to `key_secret`, `webhook_secret`, provider credentials, or raw Razorpay SDK (`import razorpay`).
  - Strict operation allowlist: `CREATE_ORDER`, `CHECKOUT`, `VERIFY`, `CANCEL`, `REFUND`. Rejects unknown operations.
  - Identity & Authorization Context Reconstruction: Verifies `tenant_id`, `agent_id`, `transaction_id`, `authorization_id`, and SHA-256 `authorization_fingerprint`.
  - Fail closed error normalization via `PaymentFailureService`. Excludes secret fields from `AgentPaymentResponse`.

- **Phase 301 — Approval Architecture (`ApprovalPolicyEngine`)**:
  - Foundational human-in-the-loop payment approval domain architecture (`ApprovalStatus`, `ApprovalPolicy`, `ApprovalContext`, `ApprovalRequest`, `ApprovalDecisionRecord`).
  - Deterministic Policy Evaluation:
    - Low Risk / Low Value -> `NOT_REQUIRED`.
    - High Risk / High Value / Review Decision -> `PENDING`.
  - Critical Security Invariant: Agents CANNOT self-approve (`ApprovalRequest` rejects `approval_status = APPROVED` at creation; `ApprovalDecisionRecord` rejects automated agent `reviewer_id`).
  - Execution Gate: Payment execution is BLOCKED while `approval_status == PENDING` or `REJECTED` or `EXPIRED` or `CANCELLED`.

## Group 18: Phases 302–303 Approval Request Engine & Review Queue Backend

- **Phase 302 — Approval Request Engine (`ApprovalRequestService`)**:
  - Authoritative service creating immutable approval request records when `ApprovalPolicyEngine` evaluates `approval_status = PENDING`.
  - Invariant Guard: All approval requests start as `PENDING`. Rejects creation with `APPROVED`, `REJECTED`, `EXPIRED`, or `CANCELLED`.
  - Identity & Authorization Binding: Binds `tenant_id`, `agent_id`, `transaction_id`, `authorization_id`, `authorization_fingerprint`, `approval_fingerprint`, and monetary parameters.
  - Idempotency & Conflict Handling: Replays existing pending request on identical idempotency key (`is_existing=True`); raises 409 Conflict (`ApprovalRequestConflictError`) if financial parameters differ.
  - Deterministic Priority Matrix: Derives priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) based on composite risk score and monetary value.

- **Phase 303 — Review Queue Backend (`ReviewQueueService`)**:
  - Backend service exposing pending approval requests to authorized review interfaces.
  - Multi-Tenant Isolation: Tenant context derived strictly from authenticated session context. Anti-enumeration returns zero items for cross-tenant query attempts.
  - Controlled Filtering: Supports filtering by `status`, `operation`, `min_priority`, and date ranges.
  - Deterministic Ordering: Primary `priority DESC` (`CRITICAL`=4, `HIGH`=3, `MEDIUM`=2, `LOW`=1), Secondary `created_at ASC`, Tertiary `approval_request_id ASC`.
  - Bounded Keyset Pagination: Cursor-based pagination enforcing maximum `page_size <= 100`. Excludes secrets (`key_secret`, `webhook_secret`) from `ReviewQueueItem`.

## Group 19: Phases 304–305 Reviewer Authorization & Approval Workflow

- **Phase 304 — Reviewer Authorization (`ReviewerAuthorizationService`)**:
  - Trusted authorization boundary evaluating: "Is this HUMAN REVIEWER authorized to perform this specific approval operation on this specific approval request?"
  - Explicit Role Capability Matrix: `REVIEWER`, `SENIOR_REVIEWER`, `APPROVAL_ADMIN` with explicit permission capabilities (`VIEW_APPROVAL_REQUEST`, `VIEW_REVIEW_QUEUE`, `APPROVE_PAYMENT`, `REJECT_PAYMENT`, `CANCEL_APPROVAL`, `VIEW_APPROVAL_AUDIT`).
  - Strict Tenant Isolation: Enforces `reviewer.tenant_id == approval_request.tenant_id`. Cross-tenant attempts fail closed (`CROSS_TENANT_ACCESS`).
  - Self-Approval Protection: `reviewer_id != agent_id`. Self-approval attempts fail closed (`SELF_APPROVAL_FORBIDDEN`).
  - Configured Monetary Limits: Enforces `requested_amount <= reviewer_authorized_limit`. Exceeded limits fail closed (`APPROVAL_LIMIT_EXCEEDED`).
  - Immutability & Fingerprint Integrity: Re-validates canonical request context and SHA-256 `approval_fingerprint`. Returns `ReviewerAuthorizationResult` with zero secret exposure.

- **Phase 305 — Approval Workflow (`ApprovalWorkflowService`)**:
  - Authoritative state machine executing state transition `PENDING -> APPROVED` when ALL authorization controls succeed.
  - State Machine Enforcement: `PENDING -> APPROVED` ONLY. Invalid transitions (`APPROVED -> APPROVED` without idempotency key, `REJECTED -> APPROVED`, `EXPIRED -> APPROVED`, `CANCELLED -> APPROVED`) fail closed.
  - Idempotency & TOCTOU Protection: Thread-safe lock prevents race conditions between concurrent reviewers. Replays identical approval commands (`is_existing=True`); parameter mismatch raises 409 Conflict (`ApprovalWorkflowConflictError`).
  - Strict Execution Boundary: DOES NOT invoke Razorpay SDK, DOES NOT create payment orders, DOES NOT mutate `PaymentStatus` (`PaymentStatusService`), DOES NOT recalculate risk. State mutation STOPS at `PENDING -> APPROVED`. Phase 309 owns downstream payment continuation.

## Group 21: Phases 308–309 Approval Audit Subsystem & Approved Payment Continuation

- **Phase 308 — Approval Audit Subsystem (`ApprovalAuditService`)**:
  - Append-only, tamper-evident audit store recording every decision point across human approval lifecycles.
  - Authoritative Audit Event Taxonomy (`ApprovalAuditEventType`): `APPROVAL_REQUEST_CREATED`, `APPROVAL_VIEWED`, `APPROVAL_APPROVED`, `APPROVAL_REJECTED`, `APPROVAL_EXPIRED`, `APPROVAL_CANCELLED`, `APPROVAL_EXECUTION_STARTED`, `APPROVAL_EXECUTION_SUCCEEDED`, `APPROVAL_EXECUTION_FAILED`, `APPROVAL_EXECUTION_BLOCKED`, `APPROVAL_REPLAYED`, `APPROVAL_CONFLICT`, `APPROVAL_AUTHORIZATION_FAILED`.
  - Immutable Event Models: `ApprovalAuditEvent` and `ApprovalAuditQueryResult` (`extra="forbid"`, `frozen=True`).
  - Cryptographic Verification: Computes deterministic SHA-256 `event_fingerprint` across canonical event fields; `verify_audit_event_integrity` detects any field tampering.
  - Multi-Tenant Isolation: Audit queries strictly scoped by trusted `tenant_id` from authenticated session context.
  - Secret Protection: Automatic redaction of sensitive credentials (`key_secret`, `webhook_secret`, `Authorization` headers, Bearer tokens, API keys) from audit metadata payloads.
  - Zero Execution Boundary: Observational only. NO `DELETE` endpoints, NO destructive deletion, NO state mutation.

- **Phase 309 — Approved Payment Continuation Subsystem (`ApprovedPaymentContinuationService`)**:
  - Controlled continuation of payment execution post-human approval.
  - Core Security Rule: **APPROVAL ≠ PAYMENT SUCCESS**. Approval grants permission to execute downstream payment initiation.
  - Strict Pre-conditions: Re-validates `approval_request.status == APPROVED`, valid reviewer authorization, approval fingerprint match, tenant match, agent match, transaction match, and financial parameter immutability (`amount`, `currency`).
  - One-Time Approval Consumption: Approval requests are consumed upon first execution trigger. Subsequent attempts return safe idempotent result (`is_existing=True`, `execution_status="EXECUTION_REPLAYED"`).
  - Idempotency & 409 Conflict: Thread-safe lock prevents TOCTOU race conditions. Reusing idempotency key with modified parameters raises `ApprovedPaymentContinuationConflictError` (HTTP 409 Conflict).
  - Razorpay SDK Isolation: Executed strictly through payment service abstraction without importing `razorpay` SDK directly.

