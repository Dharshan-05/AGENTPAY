export type PaymentStatusType =
  | 'PAID'
  | 'SETTLED'
  | 'AUTHORIZED'
  | 'CAPTURED'
  | 'PENDING'
  | 'PROCESSING'
  | 'FAILED'
  | 'DECLINED'
  | 'REFUNDED'
  | 'REVIEW'
  | 'BLOCKED';

export type PaymentMethodType = 'VISA' | 'MASTERCARD' | 'GCASH' | 'MAYA' | 'WIRE_TRANSFER' | 'AMEX';

export interface PaymentRecord {
  id: string;
  amount: string;
  rawAmount: number;
  fee: string;
  net: string;
  status: PaymentStatusType;
  method: string;
  methodType: PaymentMethodType;
  customerName: string;
  customerEmail: string;
  merchant: string;
  description: string;
  agentName: string;
  agentId: string;
  policy: string;
  riskScore: number;
  riskBand: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  agentGuardStatus: 'POLICY SECURE' | 'POLICY REVIEW' | 'POLICY VIOLATION';
  fraudGuardStatus: 'CLEAN' | 'LOW RISK' | 'MEDIUM RISK' | 'HIGH RISK';
  txnHash: string;
  timestamp: string;
  ipAddress: string;
  metadata: Record<string, string>;
}

export interface WebhookEventRecord {
  id: string;
  event: string;
  paymentId: string;
  status: 'DELIVERED' | 'FAILED' | 'RETRYING';
  statusCode: number;
  latency: string;
  attempts: number;
  timestamp: string;
}

export interface SettlementRecord {
  id: string;
  grossAmount: string;
  feeAmount: string;
  netAmount: string;
  bankDestination: string;
  status: 'SETTLED' | 'PROCESSING' | 'PENDING';
  payoutDate: string;
  txnCount: number;
}
