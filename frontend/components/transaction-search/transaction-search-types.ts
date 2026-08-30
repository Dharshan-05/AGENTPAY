'use client';
export type SearchTabType = 'MULTI_SEARCH' | 'TRANSACTIONS' | 'INTENTS' | 'CUSTOMERS' | 'AGENTS' | 'PROCESSORS' | 'FORENSICS' | 'AUDIT';
export interface SearchResultRecord {
  id: string;
  searchId: string;
  queryType: string;
  resultRef: string;
  agentId: string;
  customer: string;
  amount: string;
  processor: string;
  timestamp: string;
}
