import { InventoryControlRecord } from './inventory-control-types';
export const MOCK_INVENTORY_CONTROL: InventoryControlRecord[] = [
  { id: 'ic1', inventoryId: 'ICTRL-AGP-001', warehouseLocation: 'WH-US-EAST-1 (Virginia)', sku: 'SKU-INF-10M-V1', availableUnits: 1420, reservedUnits: 80, reorderLevel: 200, status: 'HEALTHY' },
  { id: 'ic2', inventoryId: 'ICTRL-AGP-002', warehouseLocation: 'WH-EU-WEST-1 (Frankfurt)', sku: 'SKU-SEC-ENT-ANNUAL', availableUnits: 45, reservedUnits: 15, reorderLevel: 50, status: 'LOW_STOCK' },
];
