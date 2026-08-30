import { ProductCatalogRecord } from './product-catalog-types';
export const MOCK_PRODUCT_CATALOG: ProductCatalogRecord[] = [
  { id: 'pc1', catalogId: 'PCAT-AGP-001', productName: 'Autonomous LLM Inference Token Bundle (10M)', skuVariant: 'SKU-INF-10M-V1', category: 'API_INFRASTRUCTURE', basePriceUSD: '$899.00', agentEligible: true, riskTier: 'LOW', status: 'ACTIVE' },
  { id: 'pc2', catalogId: 'PCAT-AGP-002', productName: 'AgentGuard Enterprise Security Suite', skuVariant: 'SKU-SEC-ENT-ANNUAL', category: 'SECURITY_SOFTWARE', basePriceUSD: '$14,500.00', agentEligible: true, riskTier: 'LOW', status: 'ACTIVE' },
];
