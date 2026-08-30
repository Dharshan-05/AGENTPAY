'use client';
export type FraudAnomalySignalsTabType = 'ANOMALY_SIGNALS' | 'NEURAL_SCORES' | 'GEOGRAPHIC_SPIKES' | 'AUDIT';
export interface FraudAnomalySignalRecord {
  id: string;
  signalId: string;
  transactionRef: string;
  anomalyScore: string;
  signalCategory: 'VELOCITY_SPIKE' | 'IP_GEO_MISMATCH' | 'AGENT_BEHAVIORAL_SHIFT';
  recommendedAction: 'ALLOW_WITH_MONITOR' | 'FLAG_FOR_REVIEW' | 'INSTANT_BLOCK';
  status: 'ACTIVE_MONITOR' | 'RESOLVED';
}
