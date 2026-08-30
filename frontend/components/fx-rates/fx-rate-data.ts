import { FxRecord } from './fx-rate-types';
export const MOCK_FX_RATES: FxRecord[] = [
  { id: 'f1', fxId: 'FX-AGP-001', pair: 'EUR / USD', rate: '1.0850', spread: '0.0002', volume24h: '$4.82M', status: 'ACTIVE' },
  { id: 'f2', fxId: 'FX-AGP-002', pair: 'USD / INR', rate: '83.9200', spread: '0.0050', volume24h: '$2.15M', status: 'ACTIVE' },
  { id: 'f3', fxId: 'FX-AGP-003', pair: 'GBP / USD', rate: '1.3120', spread: '0.0003', volume24h: '$1.95M', status: 'ACTIVE' },
];
