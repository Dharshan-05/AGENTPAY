'use client';
export type LoyaltyTabType = 'MEMBERS' | 'ACCRUALS' | 'REDEMPTIONS' | 'TIERS' | 'RULES' | 'REWARDS' | 'AUDIT';
export interface LoyaltyRecord {
  id: string;
  memberId: string;
  customerName: string;
  tier: 'TITANIUM' | 'PLATINUM' | 'GOLD' | 'SILVER';
  pointsBalance: number;
  lifetimePoints: number;
  status: 'ACTIVE' | 'SUSPENDED';
}
