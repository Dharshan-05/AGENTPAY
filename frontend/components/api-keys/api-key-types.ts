'use client';
export type ApiKeysTabType = 'KEYS' | 'SCOPES' | 'IP_WHITELIST' | 'KEY_ROTATION' | 'AUDIT';
export interface ApiKeyRecord {
  id: string;
  keyId: string;
  name: string;
  prefix: string;
  scopes: string;
  lastUsed: string;
  ipRestriction: string;
  status: 'ACTIVE' | 'REVOKED';
}
