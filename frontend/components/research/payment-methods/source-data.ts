import {
  PaymentInstrumentRecord, CatalogMethodTypeRecord, ProcessorCapabilityRecord,
  RoutingDecisionRecord, SecurityPostureRecord, MethodRiskRecord,
  PaymentMethodAuditEvent
} from './source-types';

export const MOCK_SOURCE_INSTRUMENTS: PaymentInstrumentRecord[] = [
  {
    id: 'pm_1', instrumentId: 'PM-AGP-001', type: 'CARD', name: 'Corporate Purchasing Visa',
    maskedIdentifier: 'VISA •••• 4821', brandOrBank: 'Visa / Chase', owner: 'Finance Ops',
    agentId: 'AGT-892', agentName: 'Procurement Agent', policyId: 'AGP-GOV-001', policyName: 'Micro-Payment Policy',
    environment: 'PRODUCTION', status: 'ACTIVE', tokenStatus: 'NETWORK_TOKEN', tokenId: 'tok_ntk_88191',
    expirationDate: '12/28', processor: 'Stripe', processorReference: 'pm_1N92X1L9921',
    riskTier: 'LOW', riskScore: 12, threeDsStatus: 'READY', avsCvvResult: 'VERIFIED',
    currency: 'USD', country: 'US', spendLimit: '$10,000.00', lastUsedAt: '2m ago',
    createdAt: '2026-01-10', updatedAt: '2026-08-30 09:14:00'
  },
  {
    id: 'pm_2', instrumentId: 'PM-AGP-002', type: 'BANK_ACCOUNT', name: 'JPMorgan Operating Direct',
    maskedIdentifier: 'BANK •••• 9921', brandOrBank: 'JPMorgan Chase', owner: 'Treasury Ops',
    agentId: 'AGT-441', agentName: 'Vendor Payment Agent', policyId: 'AGP-GOV-002', policyName: 'High-Value Settlement',
    environment: 'PRODUCTION', status: 'VERIFIED', tokenStatus: 'VAULT_SECURE', tokenId: 'tok_vlt_44120',
    expirationDate: 'N/A', processor: 'JPMorgan Direct', processorReference: 'ach_jpm_9921',
    riskTier: 'LOW', riskScore: 8, threeDsStatus: 'NOT_APPLICABLE', avsCvvResult: 'MATCH',
    currency: 'USD', country: 'US', spendLimit: '$250,000.00', lastUsedAt: '18m ago',
    createdAt: '2026-01-15', updatedAt: '2026-08-30 08:50:00'
  },
  {
    id: 'pm_3', instrumentId: 'PM-AGP-003', type: 'UPI', name: 'India Corporate VPA',
    maskedIdentifier: 'agentpay•••@hdfc', brandOrBank: 'HDFC Bank', owner: 'APAC Finance',
    agentId: 'AGT-118', agentName: 'Invoice Reconciliation Agent', policyId: 'AGP-GOV-003', policyName: 'INR Merchant Policy',
    environment: 'PRODUCTION', status: 'ACTIVE', tokenStatus: 'TOKENIZED', tokenId: 'tok_upi_11890',
    expirationDate: 'N/A', processor: 'Razorpay', processorReference: 'vpa_rzp_11890',
    riskTier: 'MEDIUM', riskScore: 38, threeDsStatus: 'READY', avsCvvResult: 'VERIFIED',
    currency: 'INR', country: 'IN', spendLimit: '₹500,000.00', lastUsedAt: '45m ago',
    createdAt: '2026-02-01', updatedAt: '2026-08-30 07:15:00'
  },
  {
    id: 'pm_4', instrumentId: 'PM-AGP-004', type: 'VIRTUAL_CARD', name: 'Ephemeral Single-Use Mastercard',
    maskedIdentifier: 'MC •••• 9901', brandOrBank: 'Mastercard / Privacy.com', owner: 'SecOps',
    agentId: 'AGT-990', agentName: 'Experimental Trading Agent', policyId: 'AGP-GOV-004', policyName: 'Strict Single-Use',
    environment: 'STAGING', status: 'RESTRICTED', tokenStatus: 'NETWORK_TOKEN', tokenId: 'tok_ntk_99010',
    expirationDate: '09/26', processor: 'Adyen', processorReference: 'pm_ady_99010',
    riskTier: 'HIGH', riskScore: 68, threeDsStatus: 'REQUIRED', avsCvvResult: 'NOT_CHECKED',
    currency: 'EUR', country: 'DE', spendLimit: '€1,500.00', lastUsedAt: '2h ago',
    createdAt: '2026-03-12', updatedAt: '2026-08-30 06:00:00'
  },
  {
    id: 'pm_5', instrumentId: 'PM-AGP-005', type: 'WALLET', name: 'Apple Pay Agent Vault',
    maskedIdentifier: 'WALLET •••• 1120', brandOrBank: 'Apple Pay / Tokenized', owner: 'Mobile Ops',
    agentId: 'AGT-301', agentName: 'Logistics Purchasing Agent', policyId: 'AGP-GOV-001', policyName: 'Micro-Payment Policy',
    environment: 'PRODUCTION', status: 'ACTIVE', tokenStatus: 'NETWORK_TOKEN', tokenId: 'tok_dpan_1120',
    expirationDate: '08/29', processor: 'Stripe', processorReference: 'wallet_str_1120',
    riskTier: 'LOW', riskScore: 14, threeDsStatus: 'READY', avsCvvResult: 'VERIFIED',
    currency: 'USD', country: 'US', spendLimit: '$5,000.00', lastUsedAt: '3h ago',
    createdAt: '2026-04-05', updatedAt: '2026-08-30 05:30:00'
  },
  {
    id: 'pm_6', instrumentId: 'PM-AGP-006', type: 'BANK_TRANSFER', name: 'Citi Wire Transfer Account',
    maskedIdentifier: 'WIRE •••• 7710', brandOrBank: 'Citibank N.A.', owner: 'Treasury Ops',
    agentId: 'AGT-441', agentName: 'Vendor Payment Agent', policyId: 'AGP-GOV-002', policyName: 'High-Value Settlement',
    environment: 'PRODUCTION', status: 'VERIFIED', tokenStatus: 'VAULT_SECURE', tokenId: 'tok_vlt_77100',
    expirationDate: 'N/A', processor: 'Citibank Direct', processorReference: 'wire_citi_77100',
    riskTier: 'LOW', riskScore: 10, threeDsStatus: 'NOT_APPLICABLE', avsCvvResult: 'MATCH',
    currency: 'USD', country: 'US', spendLimit: '$1,000,000.00', lastUsedAt: '5h ago',
    createdAt: '2026-01-20', updatedAt: '2026-08-29 22:00:00'
  },
  {
    id: 'pm_7', instrumentId: 'PM-AGP-007', type: 'TOKENIZED_CARD', name: 'Visa Network Tokenized Vault',
    maskedIdentifier: 'VISA •••• 8812', brandOrBank: 'Visa Token Service', owner: 'SecOps',
    agentId: 'AGT-892', agentName: 'Procurement Agent', policyId: 'AGP-GOV-001', policyName: 'Micro-Payment Policy',
    environment: 'PRODUCTION', status: 'ACTIVE', tokenStatus: 'NETWORK_TOKEN', tokenId: 'vts_ntk_88120',
    expirationDate: '11/30', processor: 'Stripe', processorReference: 'pm_vts_88120',
    riskTier: 'LOW', riskScore: 11, threeDsStatus: 'READY', avsCvvResult: 'VERIFIED',
    currency: 'USD', country: 'US', spendLimit: '$50,000.00', lastUsedAt: '1d ago',
    createdAt: '2026-02-15', updatedAt: '2026-08-29 18:00:00'
  },
  {
    id: 'pm_8', instrumentId: 'PM-AGP-008', type: 'BNPL', name: 'Klarna Pay-in-4 Business',
    maskedIdentifier: 'BNPL •••• 4490', brandOrBank: 'Klarna Business', owner: 'Procurement',
    agentId: 'AGT-892', agentName: 'Procurement Agent', policyId: 'AGP-GOV-005', policyName: 'Deferred Settlement',
    environment: 'SANDBOX', status: 'EXPIRING_SOON', tokenStatus: 'TOKENIZED', tokenId: 'tok_klr_44900',
    expirationDate: '09/26', processor: 'Adyen', processorReference: 'bnpl_klr_44900',
    riskTier: 'MEDIUM', riskScore: 42, threeDsStatus: 'REQUIRED', avsCvvResult: 'MATCH',
    currency: 'EUR', country: 'SE', spendLimit: '€5,000.00', lastUsedAt: '2d ago',
    createdAt: '2026-05-10', updatedAt: '2026-08-28 14:00:00'
  },
  {
    id: 'pm_9', instrumentId: 'PM-AGP-009', type: 'CARD', name: 'Amex Executive Purchasing Card',
    maskedIdentifier: 'AMEX •••• 3001', brandOrBank: 'American Express', owner: 'Executive Office',
    agentId: 'AGT-892', agentName: 'Procurement Agent', policyId: 'AGP-GOV-001', policyName: 'Micro-Payment Policy',
    environment: 'PRODUCTION', status: 'EXPIRED', tokenStatus: 'VAULT_SECURE', tokenId: 'tok_vlt_30010',
    expirationDate: '07/26', processor: 'Stripe', processorReference: 'pm_amex_30010',
    riskTier: 'HIGH', riskScore: 72, threeDsStatus: 'REQUIRED', avsCvvResult: 'MATCH',
    currency: 'USD', country: 'US', spendLimit: '$15,000.00', lastUsedAt: '30d ago',
    createdAt: '2025-08-01', updatedAt: '2026-08-01 00:00:00'
  },
  {
    id: 'pm_10', instrumentId: 'PM-AGP-010', type: 'BANK_ACCOUNT', name: 'SEPA Direct Debit Account',
    maskedIdentifier: 'IBAN •••• 8820', brandOrBank: 'Deutsche Bank', owner: 'EU Treasury',
    agentId: 'AGT-441', agentName: 'Vendor Payment Agent', policyId: 'AGP-GOV-002', policyName: 'High-Value Settlement',
    environment: 'PRODUCTION', status: 'VERIFIED', tokenStatus: 'VAULT_SECURE', tokenId: 'tok_sepa_88200',
    expirationDate: 'N/A', processor: 'Adyen', processorReference: 'sepa_db_88200',
    riskTier: 'LOW', riskScore: 15, threeDsStatus: 'NOT_APPLICABLE', avsCvvResult: 'MATCH',
    currency: 'EUR', country: 'DE', spendLimit: '€100,000.00', lastUsedAt: '3d ago',
    createdAt: '2026-03-01', updatedAt: '2026-08-27 10:00:00'
  },
  {
    id: 'pm_11', instrumentId: 'PM-AGP-011', type: 'WALLET', name: 'Google Pay Business Vault',
    maskedIdentifier: 'GPAY •••• 5510', brandOrBank: 'Google Pay / Tokenized', owner: 'Android Ops',
    agentId: 'AGT-301', agentName: 'Logistics Purchasing Agent', policyId: 'AGP-GOV-001', policyName: 'Micro-Payment Policy',
    environment: 'PRODUCTION', status: 'SUSPENDED', tokenStatus: 'NETWORK_TOKEN', tokenId: 'tok_gpay_55100',
    expirationDate: '10/27', processor: 'Stripe', processorReference: 'gpay_str_55100',
    riskTier: 'CRITICAL', riskScore: 88, threeDsStatus: 'REQUIRED', avsCvvResult: 'NOT_CHECKED',
    currency: 'USD', country: 'US', spendLimit: '$2,000.00', lastUsedAt: '4d ago',
    createdAt: '2026-04-10', updatedAt: '2026-08-26 12:00:00'
  },
  {
    id: 'pm_12', instrumentId: 'PM-AGP-012', type: 'UPI', name: 'Secondary Business VPA',
    maskedIdentifier: 'acme•••@icici', brandOrBank: 'ICICI Bank', owner: 'APAC Finance',
    agentId: 'AGT-118', agentName: 'Invoice Reconciliation Agent', policyId: 'AGP-GOV-003', policyName: 'INR Merchant Policy',
    environment: 'STAGING', status: 'REVOKED', tokenStatus: 'NOT_TOKENIZED', tokenId: 'tok_none_000',
    expirationDate: 'N/A', processor: 'Razorpay', processorReference: 'vpa_icici_000',
    riskTier: 'HIGH', riskScore: 78, threeDsStatus: 'NOT_APPLICABLE', avsCvvResult: 'NOT_CHECKED',
    currency: 'INR', country: 'IN', spendLimit: '₹100,000.00', lastUsedAt: '15d ago',
    createdAt: '2026-02-20', updatedAt: '2026-08-15 00:00:00'
  }
];

export const MOCK_CATALOG_TYPES: CatalogMethodTypeRecord[] = [
  { type: 'CARD', label: 'Credit & Debit Cards', description: 'Visa, Mastercard, Amex credit & debit cards with 3DS auth and network tokenization.', availability: 'PRODUCTION_READY', verificationMethod: 'AVS + CVV + 3DS2 Challenge', securityProfile: 'PCI-DSS SAQ-A / Network Token', supportedProcessors: ['Stripe', 'Adyen', 'JPMorgan', 'Citibank'], supportedCurrencies: ['USD', 'EUR', 'GBP', 'CAD', 'AUD'], supportedCountries: ['US', 'DE', 'GB', 'CA', 'AU'], riskRating: 'LOW', pciScope: 'OUT_OF_SCOPE' },
  { type: 'BANK_ACCOUNT', label: 'ACH / Direct Debit', description: 'Direct bank account transfers via ACH, SEPA Direct Debit, and FedNow.', availability: 'PRODUCTION_READY', verificationMethod: 'Plaid Micro-Deposits / Open Banking API', securityProfile: 'mTLS + Vault Enclave Encryption', supportedProcessors: ['JPMorgan Direct', 'Citibank Direct', 'Adyen', 'Stripe'], supportedCurrencies: ['USD', 'EUR', 'GBP'], supportedCountries: ['US', 'DE', 'GB'], riskRating: 'LOW', pciScope: 'OUT_OF_SCOPE' },
  { type: 'UPI', label: 'Unified Payments Interface', description: 'Real-time Indian instant bank payment via Virtual Payment Address (VPA).', availability: 'PRODUCTION_READY', verificationMethod: 'UPI PIN / MPIN 2FA via NPCI', securityProfile: 'HMAC-SHA256 Signed VPAs', supportedProcessors: ['Razorpay', 'Adyen'], supportedCurrencies: ['INR'], supportedCountries: ['IN'], riskRating: 'MEDIUM', pciScope: 'OUT_OF_SCOPE' },
  { type: 'WALLET', label: 'Digital Wallets', description: 'Apple Pay and Google Pay tokenized DPAN mobile wallets.', availability: 'PRODUCTION_READY', verificationMethod: 'Device Biometric (FaceID / TouchID)', securityProfile: 'EMVCo Tokenization', supportedProcessors: ['Stripe', 'Adyen'], supportedCurrencies: ['USD', 'EUR', 'GBP', 'CAD'], supportedCountries: ['US', 'DE', 'GB', 'CA'], riskRating: 'LOW', pciScope: 'OUT_OF_SCOPE' },
  { type: 'VIRTUAL_CARD', label: 'Ephemeral Virtual Cards', description: 'Single-use or merchant-locked virtual cards generated for agent autonomy.', availability: 'PRODUCTION_READY', verificationMethod: 'Pre-Approved Dynamic Spending Limits', securityProfile: 'Merchant-Locked / Auto-Expiring', supportedProcessors: ['Stripe', 'Adyen'], supportedCurrencies: ['USD', 'EUR'], supportedCountries: ['US', 'DE'], riskRating: 'LOW', pciScope: 'OUT_OF_SCOPE' },
  { type: 'BANK_TRANSFER', label: 'Wire Transfers', description: 'High-value SWIFT and Fedwire bank transfers for large vendor payouts.', availability: 'PRODUCTION_READY', verificationMethod: 'Dual-Control Admin Approval + mTLS', securityProfile: 'ISO 20022 Financial XML Signed', supportedProcessors: ['Citibank Direct', 'JPMorgan Direct'], supportedCurrencies: ['USD', 'EUR', 'GBP', 'JPY'], supportedCountries: ['US', 'DE', 'GB', 'JP'], riskRating: 'LOW', pciScope: 'OUT_OF_SCOPE' },
  { type: 'BNPL', label: 'Buy Now Pay Later', description: 'Klarna and Affirm installment payment options for commercial credit.', availability: 'STAGING_ONLY', verificationMethod: 'Soft Credit Evaluation', securityProfile: 'Merchant Credit Agreement Token', supportedProcessors: ['Adyen', 'Stripe'], supportedCurrencies: ['USD', 'EUR', 'GBP'], supportedCountries: ['US', 'SE', 'GB'], riskRating: 'MEDIUM', pciScope: 'OUT_OF_SCOPE' },
  { type: 'TOKENIZED_CARD', label: 'Visa/MC Network Tokens', description: 'Cryptographic network tokens bound to card lifecycle for zero-decline renewals.', availability: 'PRODUCTION_READY', verificationMethod: 'Visa Token Service / Mastercard MDES', securityProfile: 'Cryptogram per Transaction', supportedProcessors: ['Stripe', 'Adyen', 'JPMorgan'], supportedCurrencies: ['USD', 'EUR', 'GBP'], supportedCountries: ['US', 'DE', 'GB'], riskRating: 'LOW', pciScope: 'OUT_OF_SCOPE' }
];

export const MOCK_PROCESSOR_MATRIX: ProcessorCapabilityRecord[] = [
  { methodType: 'CARD', stripe: true, adyen: true, jpmorgan: true, citibank: true, razorpay: 'DEGRADED' },
  { methodType: 'VIRTUAL_CARD', stripe: true, adyen: true, jpmorgan: 'DEGRADED', citibank: false, razorpay: false },
  { methodType: 'BANK_ACCOUNT', stripe: true, adyen: true, jpmorgan: true, citibank: true, razorpay: false },
  { methodType: 'UPI', stripe: false, adyen: 'DEGRADED', jpmorgan: false, citibank: false, razorpay: true },
  { methodType: 'WALLET', stripe: true, adyen: true, jpmorgan: false, citibank: false, razorpay: 'DEGRADED' },
  { methodType: 'BANK_TRANSFER', stripe: 'DEGRADED', adyen: true, jpmorgan: true, citibank: true, razorpay: false },
  { methodType: 'BNPL', stripe: true, adyen: true, jpmorgan: false, citibank: false, razorpay: false },
  { methodType: 'TOKENIZED_CARD', stripe: true, adyen: true, jpmorgan: true, citibank: false, razorpay: false }
];

export const MOCK_ROUTING_DECISIONS: RoutingDecisionRecord[] = [
  { id: 'rt_1', methodId: 'PM-AGP-001', methodName: 'Corporate Purchasing Visa', agentId: 'AGT-892', requestedCurrency: 'USD', requestedCountry: 'US', riskScore: 12, selectedProcessor: 'Stripe (Primary)', fallbackProcessor: 'Adyen', status: 'OPTIMAL_ROUTE', latencyMs: 142, healthScore: 99.94, decisionReason: 'Lowest cost + 99.94% auth rate in US region', timestamp: '2026-08-30 09:14:00' },
  { id: 'rt_2', methodId: 'PM-AGP-002', methodName: 'JPMorgan Operating Direct', agentId: 'AGT-441', requestedCurrency: 'USD', requestedCountry: 'US', riskScore: 8, selectedProcessor: 'JPMorgan Direct', fallbackProcessor: 'Citibank Direct', status: 'OPTIMAL_ROUTE', latencyMs: 195, healthScore: 100.0, decisionReason: 'Direct ACH rail routing zero interchange fee', timestamp: '2026-08-30 08:50:00' },
  { id: 'rt_3', methodId: 'PM-AGP-003', methodName: 'India Corporate VPA', agentId: 'AGT-118', requestedCurrency: 'INR', requestedCountry: 'IN', riskScore: 38, selectedProcessor: 'Razorpay (Primary)', fallbackProcessor: 'Adyen India', status: 'OPTIMAL_ROUTE', latencyMs: 310, healthScore: 98.8, decisionReason: 'Native NPCI UPI connector with instant settlement', timestamp: '2026-08-30 07:15:00' },
  { id: 'rt_4', methodId: 'PM-AGP-004', methodName: 'Ephemeral Single-Use Mastercard', agentId: 'AGT-990', requestedCurrency: 'EUR', requestedCountry: 'DE', riskScore: 68, selectedProcessor: 'Adyen (Fallback)', fallbackProcessor: 'Stripe Europe', status: 'FALLBACK_TRIGGERED', latencyMs: 520, healthScore: 94.2, decisionReason: 'Stripe 3DS challenge timeout -> Switched to Adyen', timestamp: '2026-08-30 06:00:00' },
  { id: 'rt_5', methodId: 'PM-AGP-011', methodName: 'Google Pay Business Vault', agentId: 'AGT-301', requestedCurrency: 'USD', requestedCountry: 'US', riskScore: 88, selectedProcessor: 'BLOCKED', fallbackProcessor: 'NONE', status: 'ROUTE_BLOCKED', latencyMs: 0, healthScore: 0, decisionReason: 'FraudGuard critical anomaly score (88/100) -> Route terminated', timestamp: '2026-08-26 12:00:00' }
];

export const MOCK_SECURITY_RECORDS: SecurityPostureRecord[] = [
  { id: 'sec_1', instrumentId: 'PM-AGP-001', instrumentName: 'Corporate Purchasing Visa', pciScope: 'OUT_OF_SCOPE', vaultReference: 'vault_pm_••••91F2', tokenFingerprint: 'fng_ntk_sha256_7f8a9b', encryptionAlgorithm: 'AES-256-GCM + Network Token', mTLSStatus: 'ENFORCED', secretRotatedAt: '2026-08-16', lastVerifiedAt: '2026-08-30 09:14:00' },
  { id: 'sec_2', instrumentId: 'PM-AGP-002', instrumentName: 'JPMorgan Operating Direct', pciScope: 'OUT_OF_SCOPE', vaultReference: 'vault_ach_••••4412', tokenFingerprint: 'fng_ach_sha256_1a2b3c', encryptionAlgorithm: 'Hardware Security Module (HSM)', mTLSStatus: 'ENFORCED', secretRotatedAt: '2026-07-01', lastVerifiedAt: '2026-08-30 08:50:00' },
  { id: 'sec_3', instrumentId: 'PM-AGP-003', instrumentName: 'India Corporate VPA', pciScope: 'OUT_OF_SCOPE', vaultReference: 'vault_upi_••••1189', tokenFingerprint: 'fng_upi_sha256_9900aa', encryptionAlgorithm: 'NPCI Signed HMAC-SHA256', mTLSStatus: 'ENFORCED', secretRotatedAt: '2026-06-15', lastVerifiedAt: '2026-08-30 07:15:00' }
];

export const MOCK_RISK_RECORDS: MethodRiskRecord[] = [
  { id: 'rsk_1', instrumentId: 'PM-AGP-001', instrumentName: 'Corporate Purchasing Visa', agentId: 'AGT-892', riskScore: 12, riskTier: 'LOW', velocityFlag: false, geoMismatchFlag: false, deviceLinkageScore: 99, agentBehaviorRating: 'NORMAL', policyRestriction: 'Single Txn < $5,000', hitlRequired: false },
  { id: 'rsk_2', instrumentId: 'PM-AGP-004', instrumentName: 'Ephemeral Single-Use Mastercard', agentId: 'AGT-990', riskScore: 68, riskTier: 'HIGH', velocityFlag: true, geoMismatchFlag: true, deviceLinkageScore: 42, agentBehaviorRating: 'ELEVATED', policyRestriction: 'Single Txn < $1,500 + Mandatory 3DS', hitlRequired: true },
  { id: 'rsk_3', instrumentId: 'PM-AGP-011', instrumentName: 'Google Pay Business Vault', agentId: 'AGT-301', riskScore: 88, riskTier: 'CRITICAL', velocityFlag: true, geoMismatchFlag: true, deviceLinkageScore: 12, agentBehaviorRating: 'ANOMALOUS', policyRestriction: 'METHOD SUSPENDED', hitlRequired: true }
];

export const MOCK_SOURCE_AUDIT: PaymentMethodAuditEvent[] = [
  { id: 'aud_1', eventId: 'AUD-PM-001', timestamp: '2026-08-30 09:14:00', actor: 'AGT-892', actorType: 'AGENT', action: 'PAYMENT_METHOD_USED', targetRef: 'PM-AGP-001', details: 'Used PM-AGP-001 for TXN-AGP-91F2 ($4,820.00 to Acme Supplies via Stripe)', ipAddress: '10.0.4.12', auditHash: 'sha256:7f8a9b2c3d4e...' },
  { id: 'aud_2', eventId: 'AUD-PM-002', timestamp: '2026-08-30 08:50:00', actor: 'AGT-441', actorType: 'AGENT', action: 'PAYMENT_METHOD_VERIFIED', targetRef: 'PM-AGP-002', details: 'JPMorgan Direct ACH account verified with micro-deposit confirmation', ipAddress: '10.0.4.14', auditHash: 'sha256:1a2b3c4d5e6f...' },
  { id: 'aud_3', eventId: 'AUD-PM-003', timestamp: '2026-08-29 18:00:00', actor: 'dev@acme-corp.test', actorType: 'DEVELOPER', action: 'TOKEN_ROTATED', targetRef: 'PM-AGP-007', details: 'Network token rotated to vts_ntk_88120 without interrupting agent availability', ipAddress: '198.51.100.4', auditHash: 'sha256:9900aabbccdd...' },
  { id: 'aud_4', eventId: 'AUD-PM-004', timestamp: '2026-08-26 12:00:00', actor: 'AGP-GOV-AUTO', actorType: 'GOVERNANCE', action: 'PAYMENT_METHOD_SUSPENDED', targetRef: 'PM-AGP-011', details: 'Suspended PM-AGP-011 due to FraudGuard score 88/100 critical velocity flag', ipAddress: '10.0.4.10', auditHash: 'sha256:55aa66bbcc00...' }
];
