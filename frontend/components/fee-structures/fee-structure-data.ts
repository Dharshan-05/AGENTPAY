import { FeeStructureRecord } from './fee-structure-types';
export const MOCK_FEE_STRUCTURES: FeeStructureRecord[] = [
  { id: 'fs1', feeStructureId: 'FEES-AGP-001', name: 'Enterprise Interchange++ 1.8% + $0.15', model: 'INTERCHANGE_PLUS_PLUS', percentageFee: '1.80%', fixedFee: '$0.15', interchangeCap: '0.05% CAP', status: 'ACTIVE' },
  { id: 'fs2', feeStructureId: 'FEES-AGP-002', name: 'Standard Agentic Flat Rate 2.9% + $0.30', model: 'FLAT_RATE', percentageFee: '2.90%', fixedFee: '$0.30', interchangeCap: 'N/A', status: 'ACTIVE' },
];
