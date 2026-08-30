'use client';
export type SanctionsScreeningTabType = 'SANCTIONS_MATCHES' | 'OFAC_LISTS' | 'FUZZY_MATCHING' | 'BLOCKLISTS' | 'AUDIT';
export interface SanctionsScreeningRecord {
  id: string;
  screeningId: string;
  entityName: string;
  matchedList: string;
  fuzzyMatchScore: string;
  decision: 'CLEAR' | 'BLOCKED_SANCTION';
  status: 'VERIFIED_CLEAR' | 'BLOCKED';
}
