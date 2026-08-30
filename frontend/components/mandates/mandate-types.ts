'use client';
export type MandatesTabType = 'REGISTRY' | 'ACTIVE_MANDATES' | 'ACH_SEPA' | 'UPI_EMANDATE' | 'REVOKED' | 'VERIFICATION' | 'AUDIT';
export interface MandateRecord {
  id: string;
  mandateId: string;
  customer: string;
  mandateType: 'UPI_EMANDATE' | 'ACH_DIRECT_DEBIT' | 'SEPA_DIRECT_DEBIT';
  maxAmount: string;
  frequency: string;
  bankRef: string;
  status: 'ACTIVE' | 'REVOKED' | 'PENDING_AUTH';
}
