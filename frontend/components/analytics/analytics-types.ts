export interface AnalyticsMetric {
  label: string;
  value: string;
  trend: string;
  subtext: string;
  positive: boolean;
  accentColor: string;
}

export interface AgentPerformanceRecord {
  agentName: string;
  agentId: string;
  transactions: number;
  successRate: string;
  avgRisk: number;
  policyViolations: number;
  totalValue: string;
  decision: 'AUTHORIZED' | 'REVIEW' | 'BLOCKED';
}

export interface PolicyTriggerRecord {
  code: string;
  name: string;
  evaluations: number;
  triggered: number;
  blockRate: string;
}

export interface FraudSignalRecord {
  name: string;
  count: number;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  contribution: number;
}

export interface MerchantCategoryRecord {
  merchant: string;
  category: string;
  volume: string;
  riskScore: number;
  successRate: string;
  decision: 'AUTHORIZED' | 'REVIEW' | 'BLOCKED';
}

export interface RegionalActivityRecord {
  region: string;
  code: string;
  volume: string;
  transactions: number;
  riskIndex: number;
  successRate: string;
}

export interface AnomalyRecord {
  anomaly: string;
  severity: 'HIGH' | 'MEDIUM' | 'CRITICAL';
  agent: string;
  agentId: string;
  riskScore: number;
  detectedAt: string;
  status: 'INVESTIGATING' | 'REVIEW' | 'MONITORED' | 'RESOLVED';
}

export interface AnalyticsEventRecord {
  id: string;
  type: string;
  agent: string;
  riskScore: number;
  timestamp: string;
  status: 'DELIVERED' | 'PROCESSED' | 'FLAGGED';
}
