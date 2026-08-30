'use client';
export type FxExchangesTabType = 'RATES' | 'CURRENCY_PAIRS' | 'SPREADS' | 'HEDGING_RULES' | 'AUDIT';
export interface FxExchangeRecord {
  id: string;
  fxId: string;
  currencyPair: string;
  spotRate: string;
  spreadPercent: string;
  effectiveRate: string;
  lastUpdated: string;
  status: 'LIVE' | 'STALE';
}
