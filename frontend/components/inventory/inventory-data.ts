import { InventoryRecord } from './inventory-types';
export const MOCK_INVENTORY: InventoryRecord[] = [
  { id: 'iv1', inventoryId: 'INV-SKU-001', sku: 'SKU-COMPUTE-100K', productName: 'Autonomous Compute Credits (100k)', warehouse: 'US-East Cloud DC', available: 850, reserved: 50, reorderThreshold: 100, healthState: 'HEALTHY' },
  { id: 'iv2', inventoryId: 'INV-SKU-002', sku: 'SKU-GOV-ANNUAL', productName: 'Enterprise AgentGuard License', warehouse: 'US-West Core DC', available: 12, reserved: 2, reorderThreshold: 15, healthState: 'LOW_STOCK' },
];
