import { SearchResultRecord } from './transaction-search-types';
export const MOCK_SEARCH_RESULTS: SearchResultRecord[] = [
  { id: 'sr1', searchId: 'SRCH-AGP-001', queryType: 'TXN_ID', resultRef: 'TXN-AGP-91F2', agentId: 'AGT-892', customer: 'CUS-AGP-001', amount: '$781,680.00', processor: 'Stripe', timestamp: '2026-08-30 09:14:00' },
  { id: 'sr2', searchId: 'SRCH-AGP-002', queryType: 'AGENT_ID', resultRef: 'AGT-441', agentId: 'AGT-441', customer: 'CUS-AGP-002', amount: '$12,500.00', processor: 'Adyen', timestamp: '2026-08-30 08:30:00' },
];
