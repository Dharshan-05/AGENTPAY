'use client';
export type InventoryControlTabType = 'WAREHOUSES' | 'STOCK_HEALTH' | 'MOVEMENTS' | 'REORDER_THRESHOLDS' | 'DAMAGED' | 'AUDIT';
export interface InventoryControlRecord {
  id: string;
  inventoryId: string;
  warehouseLocation: string;
  sku: string;
  availableUnits: number;
  reservedUnits: number;
  reorderLevel: number;
  status: 'HEALTHY' | 'LOW_STOCK' | 'CRITICAL';
}
