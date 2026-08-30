/**
 * @agentpay/types — Shared Domain Types Baseline
 */

export type CurrencyCode = 'INR' | 'USD' | 'EUR';

export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface Tenant extends BaseEntity {
  tenant_id: string;
  name: string;
  status: 'ACTIVE' | 'SUSPENDED';
}
