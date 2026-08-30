// ============================================================
// AGENTPAY — PHASE 14B
// PAYMENT METHODS & PAYMENT METHOD OPERATIONS — PRODUCTION TYPES
// ============================================================

export type PaymentMethodTabType =
  | 'REGISTRY'
  | 'CATALOG'
  | 'CARDS_BANKS'
  | 'PROCESSORS'
  | 'ROUTING'
  | 'SECURITY'
  | 'RISK'
  | 'AUDIT';

export type InstrumentType =
  | 'CARD'
  | 'VIRTUAL_CARD'
  | 'BANK_ACCOUNT'
  | 'UPI'
  | 'WALLET'
  | 'BANK_TRANSFER'
  | 'BNPL'
  | 'TOKENIZED_CARD';

export type InstrumentStatus =
  | 'ACTIVE'
  | 'VERIFIED'
  | 'DEGRADED'
  | 'RESTRICTED'
  | 'SUSPENDED'
  | 'EXPIRING_SOON'
  | 'EXPIRED'
  | 'REVOKED';

export type TokenizationStatus =
  | 'TOKENIZED'
  | 'NETWORK_TOKEN'
  | 'VAULT_SECURE'
  | 'NOT_TOKENIZED';

export type EnvironmentType = 'PRODUCTION' | 'STAGING' | 'SANDBOX';

export interface PaymentInstrumentRecord {
  id: string;
  instrumentId: string;
  type: InstrumentType;
  name: string;
  maskedIdentifier: string;
  brandOrBank: string;
  owner: string;
  agentId: string;
  agentName: string;
  policyId: string;
  policyName: string;
  environment: EnvironmentType;
  status: InstrumentStatus;
  tokenStatus: TokenizationStatus;
  tokenId: string;
  expirationDate: string;
  processor: string;
  processorReference: string;
  riskTier: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  riskScore: number;
  threeDsStatus: 'READY' | 'REQUIRED' | 'NOT_APPLICABLE';
  avsCvvResult: 'VERIFIED' | 'MATCH' | 'NOT_CHECKED';
  currency: string;
  country: string;
  spendLimit: string;
  lastUsedAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface CatalogMethodTypeRecord {
  type: InstrumentType;
  label: string;
  description: string;
  availability: 'PRODUCTION_READY' | 'STAGING_ONLY' | 'SIMULATION';
  verificationMethod: string;
  securityProfile: string;
  supportedProcessors: string[];
  supportedCurrencies: string[];
  supportedCountries: string[];
  riskRating: 'LOW' | 'MEDIUM' | 'HIGH';
  pciScope: string;
}

export interface ProcessorCapabilityRecord {
  methodType: InstrumentType;
  stripe: boolean | 'DEGRADED';
  adyen: boolean | 'DEGRADED';
  jpmorgan: boolean | 'DEGRADED';
  citibank: boolean | 'DEGRADED';
  razorpay: boolean | 'DEGRADED';
}

export interface RoutingDecisionRecord {
  id: string;
  methodId: string;
  methodName: string;
  agentId: string;
  requestedCurrency: string;
  requestedCountry: string;
  riskScore: number;
  selectedProcessor: string;
  fallbackProcessor: string;
  status: 'OPTIMAL' | 'FALLBACK' | 'BLOCKED';
  latencyMs: number;
  healthScore: number;
  decisionReason: string;
  timestamp: string;
}

export interface SecurityPostureRecord {
  id: string;
  instrumentId: string;
  instrumentName: string;
  pciScope: 'OUT_OF_SCOPE' | 'SAQ_A' | 'SAQ_D';
  vaultReference: string;
  tokenFingerprint: string;
  encryptionAlgorithm: string;
  mTLSStatus: 'ENFORCED' | 'OPTIONAL' | 'DISABLED';
  secretRotatedAt: string;
  lastVerifiedAt: string;
}

export interface MethodRiskRecord {
  id: string;
  instrumentId: string;
  instrumentName: string;
  agentId: string;
  riskScore: number;
  riskTier: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  velocityFlag: boolean;
  geoMismatchFlag: boolean;
  deviceLinkageScore: number;
  agentBehaviorRating: 'NORMAL' | 'ELEVATED' | 'ANOMALOUS';
  policyRestriction: string;
  hitlRequired: boolean;
}

export interface PaymentMethodAuditEvent {
  id: string;
  eventId: string;
  timestamp: string;
  actor: string;
  actorType: 'DEVELOPER' | 'SYSTEM' | 'AGENT' | 'GOVERNANCE';
  action: string;
  targetRef: string;
  details: string;
  ipAddress: string;
  auditHash: string;
}

export interface PaymentMethodFilterState {
  searchQuery: string;
  type: string;
  status: string;
  processor: string;
  agent: string;
  riskTier: string;
  environment: string;
  country: string;
  currency: string;
}
