'use client';
export type InventoryTabType = 'STOCK_LEVELS' | 'WAREHOUSES' | 'RESERVATIONS' | 'REORDER_ALERTS' | 'HEALTH' | 'MOVEMENTS' | 'AUDIT';
export interface InventoryRecord {
  id: string;
  inventoryId: string;
  sku: string;
  productName: string;
  warehouse: string;
  available: number;
  reserved: number;
  reorderThreshold: number;
  healthState: 'HEALTHY' | 'LOW_STOCK' | 'CRITICAL';
}
