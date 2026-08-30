import { ChargebackAutoDefenseRecord } from './chargeback-auto-defense-types';
export const MOCK_CHARGEBACK_AUTO_DEFENSES: ChargebackAutoDefenseRecord[] = [
  { id: 'ad1', defenseId: 'ADEF-AGP-001', disputeRef: 'CHG-AGP-001', evidenceType: 'AGENT_LOGS_AND_POLICY_VERIFICATION', compiledProofHash: 'sha256:d91a...44f0', winProbability: '98.5%', status: 'SUBMITTED_WINNING' },
  { id: 'ad2', defenseId: 'ADEF-AGP-002', disputeRef: 'CHG-AGP-002', evidenceType: '3DS_CAVV_AND_AVS_MATCH', compiledProofHash: 'sha256:e41b...99c2', winProbability: '96.2%', status: 'SUBMITTED_WINNING' },
];
