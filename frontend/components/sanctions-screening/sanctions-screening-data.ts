import { SanctionsScreeningRecord } from './sanctions-screening-types';
export const MOCK_SANCTIONS_SCREENINGS: SanctionsScreeningRecord[] = [
  { id: 's1', screeningId: 'SNC-AGP-001', entityName: 'Acme Agentic Solutions LLC', matchedList: 'OFAC_SDN_LIST', fuzzyMatchScore: '0.0% (NO MATCH)', decision: 'CLEAR', status: 'VERIFIED_CLEAR' },
  { id: 's2', screeningId: 'SNC-AGP-002', entityName: 'Global AI Marketplace GmbH', matchedList: 'EU_CONSOLIDATED_LIST', fuzzyMatchScore: '0.0% (NO MATCH)', decision: 'CLEAR', status: 'VERIFIED_CLEAR' },
];
