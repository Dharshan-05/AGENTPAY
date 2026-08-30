'use client';
export type DiscountsTabType = 'RULES' | 'AUTOMATIC' | 'TIERED' | 'PROMOTIONS' | 'EXCLUSIONS' | 'APPLICATIONS' | 'AUDIT';
export interface DiscountRecord {
  id: string;
  discountId: string;
  name: string;
  type: 'PERCENTAGE' | 'FIXED_AMOUNT' | 'BUY_X_GET_Y';
  value: string;
  allocation: 'ENTIRE_ORDER' | 'SPECIFIC_PRODUCTS';
  usageCount: number;
  status: 'ACTIVE' | 'EXPIRED';
}
