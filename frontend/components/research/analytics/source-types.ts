export interface SourceKpiMetric {
  title: string;
  value: string;
  change: string;
  isPositive: boolean;
  subtext: string;
}

export interface SourceAgentRecord {
  id: string;
  name: string;
  agentId: string;
  transactions: number;
  successRate: string;
  avgRisk: number;
  policyViolations: number;
  totalValue: string;
  status: 'AUTHORIZED' | 'REVIEW' | 'BLOCKED';
}

export interface SourcePolicyRecord {
  code: string;
  name: string;
  evaluations: number;
  triggered: number;
  blockRate: string;
}

export interface SourceMerchantRecord {
  name: string;
  category: string;
  volume: string;
  riskScore: number;
  successRate: string;
  status: 'AUTHORIZED' | 'REVIEW' | 'BLOCKED';
}

export interface SourceRegionalRecord {
  region: string;
  code: string;
  volume: string;
  transactions: number;
  riskIndex: number;
  successRate: string;
}

export interface SourceAnomalyRecord {
  id: string;
  title: string;
  severity: 'HIGH' | 'MEDIUM' | 'CRITICAL';
  agent: string;
  agentId: string;
  riskScore: number;
  timestamp: string;
  status: 'INVESTIGATING' | 'REVIEW' | 'MONITORED';
}

export interface SourceEventRecord {
  id: string;
  type: string;
  agent: string;
  riskScore: number;
  timestamp: string;
  status: 'DELIVERED' | 'PROCESSED' | 'FLAGGED';
}
