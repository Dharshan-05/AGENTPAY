'use client';
export type SessionControlTabType = 'SESSIONS' | 'AUTHENTICATION' | 'IP_GEOLOCATION' | 'FRAUDGUARD_SIGNALS' | 'EXPIRED' | 'AUDIT';
export interface SessionControlRecord {
  id: string;
  sessionId: string;
  agentRef: string;
  ipAddressMasked: string;
  authMethod: 'MUTUAL_TLS' | 'JWT_BEARER';
  riskScore: number;
  status: 'ACTIVE' | 'EXPIRED' | 'REVOKED';
}
