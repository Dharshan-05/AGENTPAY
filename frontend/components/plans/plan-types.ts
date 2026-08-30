'use client';
export type PlansTabType = 'PRICING_PLANS' | 'TIERS' | 'USAGE_PRICING' | 'LIMITS' | 'ENTITLEMENTS' | 'CURRENCIES' | 'ARCHIVED' | 'AUDIT';
export interface PlanRecord {
  id: string;
  planId: string;
  name: string;
  tier: string;
  monthlyPrice: string;
  annualPrice: string;
  agentLimit: number;
  status: 'ACTIVE' | 'ARCHIVED';
}
