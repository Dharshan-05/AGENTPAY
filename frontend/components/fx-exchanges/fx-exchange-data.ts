import { FxExchangeRecord } from './fx-exchange-types';
export const MOCK_FX_EXCHANGES: FxExchangeRecord[] = [
  { id: 'fx1', fxId: 'FXEX-AGP-001', currencyPair: 'USD / EUR', spotRate: '0.9240', spreadPercent: '0.15%', effectiveRate: '0.9226', lastUpdated: '2026-08-30 18:15:00', status: 'LIVE' },
  { id: 'fx2', fxId: 'FXEX-AGP-002', currencyPair: 'USD / GBP', spotRate: '0.7810', spreadPercent: '0.15%', effectiveRate: '0.7798', lastUpdated: '2026-08-30 18:15:00', status: 'LIVE' },
];
