'use client';
export type ProductCatalogTabType = 'CATALOG_MATRIX' | 'VARIANTS' | 'MULTI_CURRENCY' | 'TAX_PROFILES' | 'AGENT_ELIGIBILITY' | 'AUDIT';
export interface ProductCatalogRecord {
  id: string;
  catalogId: string;
  productName: string;
  skuVariant: string;
  category: string;
  basePriceUSD: string;
  agentEligible: boolean;
  riskTier: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'ACTIVE' | 'ARCHIVED';
}
