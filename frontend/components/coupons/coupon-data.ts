import { CouponRecord } from './coupon-types';
export const MOCK_COUPONS: CouponRecord[] = [
  { id: 'c1', couponId: 'CPN-AGP-001', code: 'AGENTPAY-PROMO-2026', discountType: 'PERCENT', amount: '20% OFF', maxRedemptions: 500, redeemedCount: 312, status: 'ACTIVE' },
  { id: 'c2', couponId: 'CPN-AGP-002', code: 'AUTONOMOUS-50USD', discountType: 'FIXED', amount: '$50.00 OFF', maxRedemptions: 100, redeemedCount: 100, status: 'EXHAUSTED' },
];
