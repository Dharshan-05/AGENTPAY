import { DiscountRecord } from './discount-types';
export const MOCK_DISCOUNTS: DiscountRecord[] = [
  { id: 'd1', discountId: 'DSC-AGP-001', name: 'Enterprise Volume Discount 15%', type: 'PERCENTAGE', value: '15%', allocation: 'ENTIRE_ORDER', usageCount: 142, status: 'ACTIVE' },
  { id: 'd2', discountId: 'DSC-AGP-002', name: 'Agent API Kickstart $100 Off', type: 'FIXED_AMOUNT', value: '$100.00', allocation: 'SPECIFIC_PRODUCTS', usageCount: 88, status: 'ACTIVE' },
];
