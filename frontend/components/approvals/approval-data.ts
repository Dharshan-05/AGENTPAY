import { ApprovalRecord } from './approval-types';

export const MOCK_APPROVALS: ApprovalRecord[] = [
  { id: 'ap1', approvalId: 'APR-AGP-001', transactionId: 'TXN-AGP-4410', agentId: 'AGT-441', policyId: 'AGP-GOV-002', amount: '$12,500.00', riskScore: 68, requester: 'Vendor Payment Agent', approver: 'Finance Admin', slaRemaining: '14m remaining', status: 'PENDING', created: '16m ago' },
  { id: 'ap2', approvalId: 'APR-AGP-002', transactionId: 'TXN-AGP-9901', agentId: 'AGT-990', policyId: 'AGP-GOV-004', amount: '€1,500.00', riskScore: 78, requester: 'Experimental Trading Agent', approver: 'SecOps Lead', slaRemaining: 'Expired', status: 'REJECTED', created: '2h ago' },
];
