'use client';
export type FeeStructuresTabType = 'STRUCTURES' | 'INTERCHANGE_PLUS' | 'TIERED_RATES' | 'AGENT_SPLITS' | 'AUDIT';
export interface FeeStructureRecord {
  id: string;
  feeStructureId: string;
  name: string;
  model: 'INTERCHANGE_PLUS_PLUS' | 'FLAT_RATE' | 'TIERED_VOLUME';
  percentageFee: string;
  fixedFee: string;
  interchangeCap: string;
  status: 'ACTIVE' | 'ARCHIVED';
}
