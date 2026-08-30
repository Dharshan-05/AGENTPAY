'use client';
export type ChargebackAutoDefenseTabType = 'AUTO_EVIDENCE_JOBS' | 'WIN_RATE_RULES' | 'TEMPLATES' | 'AUDIT';
export interface ChargebackAutoDefenseRecord {
  id: string;
  defenseId: string;
  disputeRef: string;
  evidenceType: 'AGENT_LOGS_AND_POLICY_VERIFICATION' | '3DS_CAVV_AND_AVS_MATCH';
  compiledProofHash: string;
  winProbability: string;
  status: 'SUBMITTED_WINNING' | 'AUTO_COMPILED';
}
