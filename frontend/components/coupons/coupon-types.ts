'use client';
export type CouponsTabType = 'COUPONS' | 'SINGLE_USE' | 'VOUCHERS' | 'REDEMPTIONS' | 'AGENT_CODES' | 'LIMITS' | 'AUDIT';
export interface CouponRecord {
  id: string;
  couponId: string;
  code: string;
  discountType: 'PERCENT' | 'FIXED';
  amount: string;
  maxRedemptions: number;
  redeemedCount: number;
  status: 'ACTIVE' | 'EXHAUSTED' | 'EXPIRED';
}
