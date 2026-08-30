'use client';
export type FxTabType = 'LIVE_RATES' | 'CONVERSIONS' | 'TREASURY_HEDGING' | 'SPREADS' | 'PAIRS' | 'HISTORICAL' | 'AUDIT';
export interface FxRecord {
  id: string;
  fxId: string;
  pair: string;
  rate: string;
  spread: string;
  volume24h: string;
  status: 'ACTIVE' | 'HALTED';
}
