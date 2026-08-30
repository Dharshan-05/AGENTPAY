import { FraudAnomalySignalRecord } from './fraud-anomaly-signal-types';
export const MOCK_FRAUD_ANOMALY_SIGNALS: FraudAnomalySignalRecord[] = [
  { id: 's1', signalId: 'SIG-AGP-001', transactionRef: 'TXN-AGP-91F2', anomalyScore: '12 / 100', signalCategory: 'VELOCITY_SPIKE', recommendedAction: 'ALLOW_WITH_MONITOR', status: 'ACTIVE_MONITOR' },
  { id: 's2', signalId: 'SIG-AGP-002', transactionRef: 'TXN-AGP-88C4', anomalyScore: '18 / 100', signalCategory: 'IP_GEO_MISMATCH', recommendedAction: 'ALLOW_WITH_MONITOR', status: 'ACTIVE_MONITOR' },
];
