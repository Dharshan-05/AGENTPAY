export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
export type Decision = "ALLOW" | "BLOCK" | "REWRITE" | "FLAG" | "REVIEW";
export type ThreatLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE";
export type AgentStatus = "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "SKIPPED";

export interface DetectedSecret {
  type: string;
  label: string;
  match: string;
  redacted: string;
  position: { start: number; end: number };
  severity: Severity;
  confidence: number;
}

export interface PolicyViolation {
  policyId: string;
  policyName: string;
  regulation: string;
  category: string;
  severity: Severity;
  ruleId: string;
  reason: string;
  recommendation: string;
}

export interface AgentTraceEntry {
  agent: string;
  status: AgentStatus;
  confidence: number;
  executionTimeMs: number;
  startedAt: string;
  error?: string;
}

export interface PipelineResult {
  pipelineId: string;
  status: "COMPLETED" | "BLOCKED" | "REWRITTEN" | "FLAGGED";
  decision: Decision;
  riskScore: number;
  threatLevel: ThreatLevel;
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

export interface AuditUser {
  id: string;
  name: string;
  email: string;
  department: string;
  role: string;
}

export interface AuditRecord {
  id: string;
  promptHash: string;
  prompt: string;
  rewrittenPrompt: string | null;
  violations: PolicyViolation[];
  riskScore: number;
  threatLevel: ThreatLevel;
  policiesTriggered: string[];
  secrets: DetectedSecret[];
  decision: Decision;
  llmProvider: string | null;
  llmModel: string | null;
  timestamp: string;
  user: AuditUser | null;
}

export interface DashboardStats {
  totalPrompts: number;
  blockedPrompts: number;
  safeRequests: number;
  riskScore: number;
  activeSessions: number;
  violations24h: number;
  agentsOnline: number;
  activeIncidents: number;
  criticalIncidents: number;
  complianceHealth: number;
  detectionAccuracy: number;
  avgResponseTime: number;
  promptsTrend: number[];
  riskDistribution: { low: number; medium: number; high: number; critical: number };
  topCategories: Array<{ category: string; count: number }>;
  topViolatedPolicies: Array<{ policyName: string; count: number; regulation: string; severity: string }>;
  departmentRisk: Array<{ department: string; riskIndex: number; avgScore: number; totalPrompts: number }>;
  hourlyTrend: Array<{ hour: number; attacks: number }>;
  weeklyTrend: Array<{ day: string; attacks: number }>;
  topSecretTypes: Array<{ type: string; count: number }>;
  securityTrend: number[];
  recentEvents: AuditRecord[];
}

export interface Policy {
  id: string;
  name: string;
  description: string;
  regulation: string;
  category: string;
  severity: Severity;
  rules: unknown[];
  enabled: boolean;
  createdAt: string;
}

export interface DetectionRule {
  id: string;
  name: string;
  category: string;
  pattern: string;
  severity: Severity;
  description: string;
  enabled: boolean;
  falsePositiveCount: number;
  truePositiveCount: number;
}

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  source: string;
  acknowledged: boolean;
  resolved: boolean;
  createdAt: string;
}

export interface AgentHealth {
  id: string;
  name: string;
  responsibility: string;
  status: string;
  lastPing: string;
  responseTime: number;
  processed: number;
  successRate: number;
  memoryMb: number;
  currentTask: string;
}

export interface CopilotSuggestion {
  id: string;
  text: string;
}

export interface CopilotResponse {
  answer: string;
  data?: unknown;
  model?: string;
  tokensUsed?: number;
  simulated?: boolean;
  memory?: { count: number; recalled: string | null };
}

export interface LLMProviderStatus {
  id: string;
  configured: boolean;
  defaultModel: string;
}

export interface LLMStatus {
  providers: LLMProviderStatus[];
  defaultProvider: string;
  timestamp: string;
}

export interface ExecutiveInsight {
  id: string;
  category: 'risk' | 'trend' | 'compliance' | 'recommendation' | 'kpi';
  title: string;
  summary: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'positive';
  metric?: { label: string; value: string; delta?: string };
}

export interface PolicyRecommendation {
  id: string;
  pack: string;
  regulation: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  rationale: string;
  action: string;
}

export interface AIMeta {
  model: string | null;
  tokensUsed: number;
  latencyMs: number;
  simulated: boolean;
}

export interface AIResponse<T> extends AIMeta {
  data: T;
}

export interface ExecutiveStats {
  companySecurityScore: number;
  organizationHealth: { score: number; label: string };
  riskTrend: Array<{ point: number; score: number }>;
  riskForecast: Array<{ point: number; actual: number | null; forecast: number; lower: number; upper: number }>;
  complianceStatus: Array<{ regulation: string; score: number; status: string }>;
  complianceScoreTrend: Array<{ label: string; score: number }>;
  financialExposure: { lossAverted: number; fineExposure: number; breachCost: number };
  maturity: { score: number; level: string; label: string };
  kpis: {
    promptsAudited: number;
    threatsIntercepted: number;
    violations: number;
    activeIncidents: number;
    detectionAccuracy: number;
    avgResponseTime: number;
  };
  departmentBreakdown: Array<{
    name: string;
    riskIndex: number;
    avgScore: number;
    totalPrompts: number;
    violations: number;
    incidents: number;
    headcount: number;
  }>;
  executiveAlerts: Alert[];
  recommendations: Array<{ id: string; severity: Severity; title: string; detail: string }>;
  agentsOnline: number;
  timestamp: string;
}

export interface SocStats {
  threatMap: Array<{
    id: string;
    city: string;
    lat: number;
    lng: number;
    severity: Severity;
    decision: Decision;
    risk: number;
    count: number;
  }>;
  stream: Array<{
    id: string;
    user: string;
    department: string;
    action: Decision;
    risk: number;
    prompt: string;
    provider: string;
    timestamp: string;
    ts: number;
  }>;
  agentActivity: Array<{ agent: string; active: number; idle: number }>;
  incidentQueue: Array<{ id: string; title: string; risk: number; department: string; status: string; age: number }>;
  processingQueue: Array<{ id: string; prompt: string; stage: string; pct: number }>;
  investigations: Array<{ id: string; title: string; assignee: string; progress: number; risk: number }>;
  systemHealth: Record<string, { label: string; status: string; value?: string; latency?: string }>;
  criticalAlert: { title: string; risk: number; department: string; prompt: string; decision: Decision } | null;
  regions: Array<{
    city: string;
    code: string;
    lat: number;
    lng: number;
    phase: "PULSE" | "ROUTING" | "CONTAINING" | "RESOLVED";
    severity: Severity;
    attacks: number;
    active: number;
    containing: number;
    resolved: number;
    lastSeen: string;
  }>;
  counters: {
    threats: number;
    agents: number;
    latency: number;
    blockedPrompts: number;
    protectedRecords: number;
    activeAttacks: number;
  };
  throughput: Array<{ t: number; pps: number }>;
  ticker: Array<{ id: string; text: string; decision: Decision; risk: number; ts: number }>;
  totalIncidents: number;
  timestamp: string;
}

export interface TwinDepartment {
  name: string;
  people: number;
  riskIndex: number;
  avgScore: number;
  totalPrompts: number;
  violations: number;
  incidents: number;
  policies: number;
  policyNames?: string[];
  riskLevel: "HIGH" | "MEDIUM" | "LOW" | "SAFE";
  complianceScore: number;
  color: string;
  recentIncidents: Array<{ id: string; title: string; risk: number; time: string }>;
  commonViolations: string[];
  improvements: string[];
  trend: Array<{ day: string; score: number }>;
  heatmap: Array<{ regulation: string; score: number }>;
  users: Array<{ name: string; prompts: number; risky: number; score: number }>;
}

export interface TwinStats {
  departments: TwinDepartment[];
  timestamp: string;
}

export interface AnalyticsStats {
  monthlyThreats: Array<{ label: string; blocked: number; allowed: number }>;
  weeklyThreats: Array<{ label: string; threats: number }>;
  hourlyAttacks: Array<{ hour: number; attacks: number }>;
  departmentComparison: Array<{ department: string; riskIndex: number; avgScore: number }>;
  policyComparison: Array<{ policyName: string; count: number }>;
  riskEvolution: Array<{ point: number; score: number }>;
  detectionDistribution: Array<{ type: string; count: number }>;
  agentLatency: Array<{ agent: string; latency: number }>;
  pipelineDuration: Array<{ label: number; ms: number }>;
  complianceTrend: Array<{ label: string; v: number }>;
  riskForecast: Array<{ point: number; actual: number | null; forecast: number; lower: number; upper: number }>;
  incidentHeatmap: Array<{ day: number; hour: number; value: number }>;
  policyEffectiveness: Array<{ policyName: string; detected: number; prevented: number; effectiveness: number }>;
  detectionAccuracyTrend: Array<{ label: string; accuracy: number }>;
  complianceScoreTrend: Array<{ label: string; score: number }>;
  timestamp: string;
}

export interface ExplainDecision {
  id: string;
  prompt: string;
  decision: Decision;
  riskScore: number;
  threatLevel: ThreatLevel;
  timestamp: string;
  user: string;
  department: string;
  confidence: number;
  recommendation: string;
  agentContributions: Array<{
    agent: string;
    role: string;
    status: "EXECUTED" | "SKIPPED" | "TRIGGERED";
    confidence: number;
    contribution: number;
  }>;
  riskFactors: Array<{ label: string; weight: number; detail: string; tone: string }>;
  policyFactors: Array<{
    policyName: string;
    regulation: string;
    severity: Severity;
    reason: string;
    ruleId: string;
  }>;
  reasoningTimeline: Array<{ step: string; detail: string; ts: number }>;
}

export interface ExplainStats {
  decisions: ExplainDecision[];
  summary: {
    total: number;
    blocked: number;
    rewritten: number;
    flagged: number;
    allowed: number;
    avgRisk: number;
    topAgent: string;
    topPolicy: string;
  };
  timestamp: string;
}

export interface SystemStats {
  version: string;
  build: string;
  deployment: string;
  region: string;
  uptimeSeconds: number;
  cluster: { nodes: number; status: string; drift: string };
  apiLatency: number;
  memoryMb: number;
  memoryTotalMb: number;
  cpuPct: number;
  queueDepth: number;
  threatFeed: string;
  websocket: string;
  redis: string;
  database: string;
  replicas: number;
  pods: number;
  podsHealthy: string;
  canary: string;
}

export type IncidentSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type IncidentStatus = "TRIAGE" | "INVESTIGATING" | "CONTAINED" | "RESOLVED";

export interface IncidentNote {
  id: string;
  author: string;
  body: string;
  createdAt: string;
  pinned?: boolean;
}

export interface IncidentTimelineEntry {
  id: string;
  at: string;
  event: string;
  detail: string;
  actor: string;
  kind: "SYSTEM" | "ACTION" | "NOTE" | "ALERT";
}

export interface IncidentEvidence {
  id: string;
  label: string;
  value: string;
  kind: "PROMPT" | "PATTERN" | "POLICY" | "NETWORK" | "FILE" | "LOG";
}

export interface MitreTechnique {
  id: string;
  name: string;
  tactic: string;
}

export interface RiskTrendPoint {
  t: string;
  score: number;
}

export interface Incident {
  id: string;
  title: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  owner: string | null;
  department: string;
  prompt: string;
  riskScore: number;
  decision: Decision;
  slaMinutes: number;
  createdAt: string;
  escalated: boolean;
  notes: IncidentNote[];
  timeline: IncidentTimelineEntry[];
  evidence: IncidentEvidence[];
  mitreAttack: MitreTechnique[];
  relatedPolicies: string[];
  relatedUsers: string[];
  riskTrend: RiskTrendPoint[];
  aiRecommendation: string;
  relatedPrompts?: Array<{
    id: string;
    user: string;
    department: string;
    prompt: string;
    risk: number;
    decision: Decision;
    at: string;
    relation: "same-user" | "same-department" | "repeat-attempt" | "cleaned";
  }>;
}

export interface ThreatAdvisory {
  id: string;
  source: "CISA" | "MITRE" | "OWASP" | "GitHub" | "OpenAI" | "Microsoft";
  title: string;
  description: string;
  severity: Severity;
  cvss: number;
  published: string;
  affected: string;
  status: "ACTIVE" | "WATCHING" | "RESOLVED";
  cve?: string;
  tactic?: string;
  mitigation: string;
  relevance: string;
}

export interface AnalystPresence {
  id: string;
  name: string;
  role: string;
  status: "ONLINE" | "AWAY" | "OFFLINE";
  location: string;
  team: string;
  lastSeen: string;
  incident: string | null;
  emoji?: string;
}
