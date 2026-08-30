import { ProductRecord } from './product-types';
export const MOCK_PRODUCTS: ProductRecord[] = [
  { id: 'p1', productId: 'PRD-AGP-001', name: 'Autonomous Compute Credits (100k Units)', sku: 'SKU-COMPUTE-100K', type: 'AGENT_API', price: '$499.00', currency: 'USD', taxCategory: 'DIGITAL_SERVICES', status: 'ACTIVE' },
  { id: 'p2', productId: 'PRD-AGP-002', name: 'Enterprise AgentGuard License (Annual)', sku: 'SKU-GOV-ANNUAL', type: 'DIGITAL_SERVICE', price: '$12,500.00', currency: 'USD', taxCategory: 'SOFTWARE_LICENSE', status: 'ACTIVE' },
];
