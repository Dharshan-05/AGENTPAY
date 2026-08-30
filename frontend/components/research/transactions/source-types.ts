// ============================================================
// AGENTPAY — PHASE 12A
// TRANSACTION OPERATIONS — SOURCE TYPES
// Research baseline type definitions
// ============================================================

// ---- TAB NAVIGATION ----
export type TransactionSourceTabType =
  | 'REGISTRY'
  | 'INTENTS'
  | 'LIFECYCLE'
  | 'REFUNDS'
  | 'EVENTS'
  | 'AUDIT';

// ---- PAYMENT STATUS ----
export type PaymentStatus =
  | 'PENDING'
  | 'AUTHORIZED'
  | 'CAPTURED'
  | 'SETTLED'
  | 'FAILED'
  | 'CANCELLED'
  | 'REFUNDED'
  | 'PARTIALLY_REFUNDED'
  | 'DISPUTED'
  | 'REQUIRES_ACTION'
  | 'UNDER_REVIEW'
  | 'BLOCKED';

// ---- RISK TIER ----
export type RiskTier = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

// ---- PAYMENT METHOD ----
export type PaymentMethodType =
  | 'VIRTUAL_CARD'
  | 'BANK_TRANSFER'
  | 'ACH'
  | 'CARD'
  | 'UPI'
  | 'WALLET'
  | 'NET_BANKING'
  | 'PAY_LATER';

// ---- REFUND STATUS ----
export type RefundStatus = 'REQUESTED' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'PARTIAL';

// ---- DELIVERY STATUS ----
export type DeliveryStatus = 'DELIVERED' | 'PENDING' | 'FAILED' | 'RETRYING';

// ---- LIFECYCLE STEP STATUS ----
export type LifecycleStepStatus = 'COMPLETED' | 'ACTIVE' | 'PENDING' | 'FAILED' | 'SKIPPED';

// ---- TRANSACTION REGISTRY RECORD ----
export interface SourceTransactionRecord {
  id: string;
  transactionId: string;
  paymentIntentId: string;
  agentId: string;
  agentName: string;
  merchant: string;
  customer: string;
  requestedAmount: string;
  authorizedAmount: string;
  capturedAmount: string;
  currency: string;
  paymentMethod: PaymentMethodType;
  paymentMethodDetail: string;
  processor: string;
  processorReference: string;
  status: PaymentStatus;
  riskScore: number;
  riskTier: RiskTier;
  policyBinding: string;
  policyDecision: string;
  requiresHumanApproval: boolean;
  settlementId?: string;
  disputeId?: string;
  environment: 'PRODUCTION' | 'STAGING' | 'SANDBOX';
  region: string;
  createdTimestamp: string;
  updatedTimestamp: string;
  authorizationCode?: string;
  responseCode: string;
  attemptCount: number;
}

// ---- PAYMENT INTENT ----
export type PaymentIntentStatus =
  | 'CREATED'
  | 'REQUIRES_AUTHORIZATION'
  | 'REQUIRES_ACTION'
  | 'AUTHORIZED'
  | 'CAPTURED'
  | 'PARTIALLY_CAPTURED'
  | 'FAILED'
  | 'CANCELLED'
  | 'REFUNDED'
  | 'PARTIALLY_REFUNDED'
  | 'DISPUTED';

export type PaymentIntentType =
  | 'AUTONOMOUS_CARD_PAYMENT'
  | 'MERCHANT_PAYOUT_BATCH'
  | 'VENDOR_INVOICE_CLEARING'
  | 'SUBSCRIPTION_RENEWAL'
  | 'REFUND_ISSUANCE';

export interface SourcePaymentIntent {
  id: string;
  intentId: string;
  transactionId: string;
  agentId: string;
  agentName: string;
  intentType: PaymentIntentType;
  requestedAmount: string;
  authorizedAmount: string;
  capturedAmount: string;
  currency: string;
  merchant: string;
  customer: string;
  status: PaymentIntentStatus;
  policyId: string;
  policyDecision: string;
  riskScore: number;
  riskTier: RiskTier;
  requiresHumanApproval: boolean;
  humanApprovalStatus?: 'PENDING' | 'APPROVED' | 'REJECTED';
  expirationTime: string;
  createdAt: string;
  updatedAt: string;
  processor: string;
  paymentMethod: PaymentMethodType;
  threeDsStatus?: 'AUTHENTICATED' | 'FAILED' | 'NOT_REQUIRED';
}

// ---- PAYMENT ATTEMPT ----
export interface SourcePaymentAttempt {
  id: string;
  attemptId: string;
  transactionId: string;
  attemptNumber: number;
  processor: string;
  connector: string;
  route: string;
  requestedAmount: string;
  status: PaymentStatus;
  responseCode: string;
  responseMessage: string;
  latencyMs: number;
  processorFee: string;
  processorReference: string;
  timestamp: string;
  errorCode?: string;
  errorMessage?: string;
}

// ---- AUTHORIZATION ----
export interface SourceAuthorization {
  authorizationId: string;
  transactionId: string;
  requestedAmount: string;
  authorizedAmount: string;
  authorizationCode: string;
  processor: string;
  timestamp: string;
  threeDsStatus: string;
  avsResult: string;
  cvvResult: string;
  policyDecision: string;
  riskDecision: string;
  humanApproval?: string;
}

// ---- CAPTURE ----
export interface SourceCapture {
  captureId: string;
  transactionId: string;
  captureType: 'FULL' | 'PARTIAL';
  capturedAmount: string;
  originalAmount: string;
  processor: string;
  status: 'CAPTURED' | 'PARTIALLY_CAPTURED' | 'FAILED';
  settlementReference?: string;
  timestamp: string;
}

// ---- REFUND ----
export interface SourceRefundRecord {
  id: string;
  refundId: string;
  originalTransactionId: string;
  agentId: string;
  agentName: string;
  requestedAmount: string;
  processedAmount: string;
  currency: string;
  reason: 'DUPLICATE_CHARGE' | 'POLICY_VIOLATION' | 'CANCELLED_SERVICE' | 'AGENT_UNAUTHORIZED' | 'CUSTOMER_REQUEST' | 'FRAUD';
  reasonDetail: string;
  status: RefundStatus;
  processor: string;
  processorReference: string;
  requestedTimestamp: string;
  completedTimestamp?: string;
  requestedBy: string;
}

// ---- TRANSACTION EVENT ----
export type EventType =
  | 'PAYMENT_INTENT.CREATED'
  | 'AGENT.AUTHENTICATED'
  | 'CAPABILITY.VERIFIED'
  | 'POLICY.EVALUATED'
  | 'RISK.SCORED'
  | 'AUTHORIZATION.REQUESTED'
  | 'AUTHORIZATION.APPROVED'
  | 'AUTHORIZATION.FAILED'
  | 'PAYMENT.CAPTURED'
  | 'PAYMENT.FAILED'
  | 'PROCESSOR.CONFIRMED'
  | 'WEBHOOK.DELIVERED'
  | 'WEBHOOK.FAILED'
  | 'SETTLEMENT.MATCHED'
  | 'REFUND.REQUESTED'
  | 'REFUND.COMPLETED'
  | 'DISPUTE.OPENED';

export interface SourceTransactionEvent {
  id: string;
  eventId: string;
  transactionId: string;
  eventType: EventType;
  sourceGateway: string;
  timestamp: string;
  latencyMs: number;
  deliveryStatus: DeliveryStatus;
  retryCount: number;
  payload?: string;
  responseStatus?: number;
  auditHash: string;
}

// ---- TRANSACTION RISK ----
export interface SourceTransactionRisk {
  transactionId: string;
  riskScore: number;
  riskTier: RiskTier;
  velocityFlag: boolean;
  geoRiskFlag: boolean;
  deviceRiskFlag: boolean;
  agentRiskFlag: boolean;
  fraudSignals: string[];
  policyViolations: string[];
  evaluatedAt: string;
  evaluatedBy: string;
}

// ---- TRANSACTION POLICY ----
export interface SourceTransactionPolicy {
  transactionId: string;
  policyId: string;
  policyName: string;
  decision: 'APPROVED' | 'BLOCKED' | 'HITL_REVIEW' | 'CONDITIONAL';
  spendLimit: string;
  appliedRule: string;
  approvalRequired: boolean;
  evaluatedAt: string;
  decisionReason: string;
}

// ---- LIFECYCLE STEP ----
export interface LifecycleStep {
  stepNumber: number;
  stepId: string;
  label: string;
  description: string;
  status: LifecycleStepStatus;
  timestamp?: string;
  latencyMs?: number;
  actor: string;
  metadata?: Record<string, string>;
}

// ---- TRANSACTION METADATA ----
export interface TransactionMetadataEntry {
  key: string;
  value: string;
  source: string;
  createdAt: string;
}

// ---- TRANSACTION PARTICIPANT ----
export interface TransactionParticipant {
  role: 'AGENT' | 'MERCHANT' | 'CUSTOMER' | 'PROCESSOR';
  id: string;
  name: string;
  region?: string;
  accountRef?: string;
}

// ---- FILTER STATE ----
export interface TransactionFilterState {
  searchQuery: string;
  status: string;
  processor: string;
  paymentMethod: string;
  riskTier: string;
  agent: string;
  environment: string;
  dateRange: string;
}

// ---- FULL TRANSACTION DETAIL ----
export interface SourceTransactionDetail extends SourceTransactionRecord {
  authorization?: SourceAuthorization;
  capture?: SourceCapture;
  attempts: SourcePaymentAttempt[];
  events: SourceTransactionEvent[];
  risk: SourceTransactionRisk;
  policy: SourceTransactionPolicy;
  metadata: TransactionMetadataEntry[];
  participants: TransactionParticipant[];
  lifecycle: LifecycleStep[];
  refunds: SourceRefundRecord[];
}
