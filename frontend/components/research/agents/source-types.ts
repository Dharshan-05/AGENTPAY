export type AgentSourceTabType =
  | 'REGISTRY'
  | 'EXECUTIONS'
  | 'PERMISSIONS'
  | 'SECURITY';

export interface SourceAgentRecord {
  id: string;
  agentId: string;
  name: string;
  type: 'AUTONOMOUS' | 'SUPERVISED' | 'WORKFLOW' | 'SERVICE' | 'ANALYTICAL' | 'PAYMENT' | 'RECONCILIATION';
  owner: string;
  environment: 'PRODUCTION' | 'STAGING' | 'SANDBOX' | 'DEVELOPMENT';
  status: 'ACTIVE' | 'IDLE' | 'PAUSED' | 'SUSPENDED' | 'DEGRADED' | 'ERROR' | 'OFFLINE' | 'PROVISIONING';
  riskTier: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  policyBinding: string;
  lastActive: string;
  transactionCount: number;
  healthScore: number;
  credentialRotationDays: number;
}

export interface SourceAgentExecution {
  id: string;
  executionId: string;
  agentId: string;
  intent: string;
  action: string;
  policy: string;
  riskScore: number;
  result: 'AUTHORIZED' | 'BLOCKED' | 'REVIEW' | 'FAILED' | 'COMPLETED';
  latencyMs: number;
  timestamp: string;
}

export interface SourceAgentPermissionRecord {
  id: string;
  agentId: string;
  resource: 'PAYMENTS' | 'AGENTS' | 'AGENTGUARD' | 'FRAUDGUARD' | 'ANALYTICS' | 'DEVELOPERS' | 'RECONCILIATION';
  capability: string;
  scope: 'READ' | 'WRITE' | 'EXECUTE' | 'ADMIN';
  policyRule: string;
  status: 'GRANTED' | 'REVOKED' | 'CONDITIONAL';
}

export interface SourceAgentSecurityRecord {
  id: string;
  agentId: string;
  credentialType: string;
  mTLSCertificateStatus: 'VALID' | 'ROTATION_DUE' | 'REVOKED';
  keyFingerprint: string;
  lastAuthTimestamp: string;
  suspensionReason?: string;
  auditHash: string;
}
