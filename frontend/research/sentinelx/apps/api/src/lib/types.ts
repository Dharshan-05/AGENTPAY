export const Severity = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
  INFO: 'INFO',
} as const;

export type SeverityLevel = (typeof Severity)[keyof typeof Severity];
export type SeverityType = SeverityLevel;

export const Decision = {
  ALLOW: 'ALLOW',
  BLOCK: 'BLOCK',
  REWRITE: 'REWRITE',
  FLAG: 'FLAG',
  REVIEW: 'REVIEW',
} as const;

export type DecisionType = (typeof Decision)[keyof typeof Decision];

export const ThreatLevel = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
  SAFE: 'SAFE',
} as const;

export type ThreatLevelType = (typeof ThreatLevel)[keyof typeof ThreatLevel];

export const AgentStatus = {
  PENDING: 'PENDING',
  RUNNING: 'RUNNING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  SKIPPED: 'SKIPPED',
} as const;

export type AgentStatusType = (typeof AgentStatus)[keyof typeof AgentStatus];

export const SecretCategory = {
  API_KEY: 'API_KEY',
  OPENAI_KEY: 'OPENAI_KEY',
  JWT: 'JWT',
  PASSWORD: 'PASSWORD',
  AWS_CREDENTIAL: 'AWS_CREDENTIAL',
  AZURE_CREDENTIAL: 'AZURE_CREDENTIAL',
  GCP_CREDENTIAL: 'GCP_CREDENTIAL',
  SSH_KEY: 'SSH_KEY',
  PEM_CERT: 'PEM_CERT',
  DATABASE_URL: 'DATABASE_URL',
  MONGO_URI: 'MONGO_URI',
  SQL_CREDENTIAL: 'SQL_CREDENTIAL',
  CREDIT_CARD: 'CREDIT_CARD',
  AADHAAR: 'AADHAAR',
  PAN: 'PAN',
  EMAIL: 'EMAIL',
  PHONE: 'PHONE',
  EMPLOYEE_ID: 'EMPLOYEE_ID',
  SOURCE_CODE: 'SOURCE_CODE',
  INTERNAL_URL: 'INTERNAL_URL',
  OAUTH_TOKEN: 'OAUTH_TOKEN',
  SSN: 'SSN',
  IP_ADDRESS: 'IP_ADDRESS',
  IBAN: 'IBAN',
  SWIFT: 'SWIFT',
  BITCOIN: 'BITCOIN',
  PRIVATE_KEY: 'PRIVATE_KEY',
  SALARY: 'SALARY',
  HEALTH_RECORD: 'HEALTH_RECORD',
  FINANCIAL_DOC: 'FINANCIAL_DOC',
  LEGAL_DOC: 'LEGAL_DOC',
  PII: 'PII',
  CODE_SECRET: 'CODE_SECRET',
  SESSION_TOKEN: 'SESSION_TOKEN',
  GOOGLE_API_KEY: 'GOOGLE_API_KEY',
  STRIPE_KEY: 'STRIPE_KEY',
  GITHUB_TOKEN: 'GITHUB_TOKEN',
  SLACK_TOKEN: 'SLACK_TOKEN',
} as const;

export type SecretCategoryType = (typeof SecretCategory)[keyof typeof SecretCategory];

export interface DetectedSecret {
  type: SecretCategoryType;
  label: string;
  match: string;
  redacted: string;
  position: { start: number; end: number };
  severity: SeverityLevel;
  confidence: number;
}

export interface AgentResult<T = unknown> {
  status: AgentStatusType;
  confidence: number;
  executionTimeMs: number;
  output: T;
  error?: string;
}

export interface InspectorOutput {
  language: string;
  intent: string;
  topicCategory: string;
  dataSensitivity: number;
  containsSensitiveData: boolean;
  wordCount: number;
}

export interface PolicyViolation {
  policyId: string;
  policyName: string;
  regulation: string;
  category: string;
  severity: SeverityLevel;
  reason: string;
  ruleId: string;
  recommendation: string;
}

export interface RiskAssessment {
  score: number;
  threatLevel: ThreatLevelType;
  confidence: number;
  businessImpact: string;
  contributingFactors: Array<{ factor: string; weight: number; severity: SeverityLevel }>;
  recommendation: string;
}

export interface PipelineRequest {
  prompt: string;
  userId?: string;
  ipAddress?: string;
  sessionId?: string;
  provider?: string;
  model?: string;
}

export interface PipelineResult {
  pipelineId: string;
  status: 'COMPLETED' | 'BLOCKED' | 'REWRITTEN' | 'FLAGGED';
  decision: DecisionType;
  riskScore: number;
  threatLevel: ThreatLevelType;
  violations: PolicyViolation[];
  secrets: DetectedSecret[];
  originalPrompt: string;
  rewrittenPrompt: string | null;
  agentTrace: AgentTraceEntry[];
  auditLogId: string;
  provider: string;
  model: string;
  latencyMs: number;
}

export interface AgentTraceEntry {
  agent: string;
  status: AgentStatusType;
  confidence: number;
  executionTimeMs: number;
  startedAt: string;
  output?: unknown;
  error?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  department: string;
}

export interface AuditRecord {
  id: string;
  promptHash: string;
  prompt: string;
  rewrittenPrompt: string | null;
  violations: PolicyViolation[];
  riskScore: number;
  threatLevel: ThreatLevelType;
  policiesTriggered: string[];
  secrets: DetectedSecret[];
  decision: DecisionType;
  llmProvider: string | null;
  llmModel: string | null;
  timestamp: string;
  user: User | null;
}

export interface DashboardStats {
  totalPrompts: number;
  blockedPrompts: number;
  riskScore: number;
  threatLevel: ThreatLevelType;
  activeSessions: number;
  violations24h: number;
  detectionRate: number;
  agentsOnline: number;
  promptsTrend: number[];
  riskDistribution: { low: number; medium: number; high: number; critical: number };
  topCategories: Array<{ category: string; count: number }>;
  recentEvents: AuditRecord[];
}

export interface CopilotMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  data?: unknown;
  timestamp: string;
}
