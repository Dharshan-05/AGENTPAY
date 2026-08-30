import { ChargebackRecord } from './chargeback-types';
export const MOCK_CHARGEBACKS: ChargebackRecord[] = [
  { id: 'ch1', disputeId: 'CHG-AGP-001', txnRef: 'TXN-AGP-91F2', agentRef: 'AGT-892', disputeAmount: '$1,250.00', reasonCode: 'UNAUTHORIZED_AGENT_CLAIM', evidenceDueDate: '2026-09-05', status: 'EVIDENCE_SUBMITTED' },
  { id: 'ch2', disputeId: 'CHG-AGP-002', txnRef: 'TXN-AGP-4410', agentRef: 'AGT-441', disputeAmount: '€450.00', reasonCode: 'DUPLICATE_PROCESSING', evidenceDueDate: '2026-09-12', status: 'UNDER_REVIEW' },
];
