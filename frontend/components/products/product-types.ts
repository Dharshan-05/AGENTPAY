'use client';
export type ProductsTabType = 'CATALOG' | 'SKUS' | 'PRICING' | 'TAX_CATEGORIES' | 'INVENTORY' | 'MERCHANTS' | 'AUDIT';
export interface ProductRecord {
  id: string;
  productId: string;
  name: string;
  sku: string;
  type: 'PHYSICAL' | 'DIGITAL_SERVICE' | 'AGENT_API';
  price: string;
  currency: string;
  taxCategory: string;
  status: 'ACTIVE' | 'ARCHIVED';
}
