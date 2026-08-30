import type {
  AgentHealth,
  AIResponse,
  Alert,
  AnalystPresence,
  AnalyticsStats,
  AuditRecord,
  CopilotResponse,
  CopilotSuggestion,
  DashboardStats,
  DetectionRule,
  ExecutiveInsight,
  ExecutiveStats,
  ExplainStats,
  Incident,
  IncidentStatus,
  LLMStatus,
  PipelineResult,
  Policy,
  PolicyRecommendation,
  SocStats,
  SystemStats,
  ThreatAdvisory,
  TwinStats,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001";

import { getApiToken } from "@/lib/auth-token";

function getAuthToken(): string | null {
  return getApiToken();
}

export class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.code = status === 401 ? 'AUTH_REQUIRED' : status === 403 ? 'FORBIDDEN' : status === 404 ? 'NOT_FOUND' : status >= 500 ? 'SERVER_ERROR' : 'API_ERROR';
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, init?: RequestInit & { timeout?: number }): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "cache-control": "no-cache",
  };

  const token = getAuthToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const timeoutMs = init?.timeout ?? 10000; // default 10s
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(`${API_BASE}/api${path}`, {
      headers,
      ...init,
      signal: controller.signal,
    });
    clearTimeout(id);
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      let msg = body;
      try { msg = JSON.parse(body).error || body; } catch {}
      throw new ApiError(res.status, msg || `HTTP ${res.status}`);
    }
    return (await res.json()) as T;
  } catch (error) {
    clearTimeout(id);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(408, 'REQUEST_TIMEOUT');
    }
    if (error instanceof ApiError) throw error;
    throw new ApiError(0, 'NETWORK_ERROR');
  }
}

export const api = {
  me: () =>
    request<{
      id: string
      email: string
      name: string
      role: string
      picture?: string | null
      provider?: string
      emailVerified?: boolean
      lastLoginAt?: string | null
    }>("/auth/me"),

  scan: (prompt: string, provider = "openai") =>
    request<PipelineResult>("/scan", {
      method: "POST",
      body: JSON.stringify({ prompt, provider }),
    }),

  dashboard: () => request<DashboardStats>("/dashboard"),

  audit: (params?: { page?: number; search?: string; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.page) q.set("page", String(params.page));
    if (params?.limit) q.set("limit", String(params.limit));
    if (params?.search) q.set("search", params.search);
    return request<{ total: number; page: number; limit: number; records: AuditRecord[] }>(
      `/audit${q.size ? `?${q}` : ""}`,
    );
  },

  auditById: (id: string) => request<AuditRecord>(`/audit/${id}`),

  policies: () => request<Policy[]>("/policies"),
  rules: () => request<DetectionRule[]>("/rules"),
  alerts: () => request<Alert[]>("/alerts"),
  ackAlert: (id: string) =>
    request<Alert>(`/alerts/${id}/ack`, { method: "POST" }),
  settings: () => request<Record<string, string>>("/settings"),
  agents: () => request<AgentHealth[]>("/agents/health"),

  copilotSuggestions: () => request<CopilotSuggestion[]>("/copilot/suggestions"),
  copilot: (message: string, history?: Array<{ role: "user" | "assistant"; content: string }>, sessionId?: string) =>
    request<CopilotResponse>("/copilot", {
      method: "POST",
      body: JSON.stringify({ message, history: history ?? [], sessionId }),
    }),

  incidents: (params?: { severity?: string; status?: string }) => {
    const q = new URLSearchParams();
    if (params?.severity) q.set("severity", params.severity);
    if (params?.status) q.set("status", params.status);
    return request<{ incidents: Incident[]; stats: { open: number; critical: number; breached: number } }>(
      `/incidents${q.size ? `?${q}` : ""}`,
    );
  },
  incident: (id: string) => request<Incident>(`/incidents/${id}`),
  incidentNote: (id: string, body: string, author?: string) =>
    request<Incident>(`/incidents/${id}/notes`, {
      method: "POST",
      body: JSON.stringify({ body, author }),
    }),
  incidentAssign: (id: string, owner: string) =>
    request<Incident>(`/incidents/${id}/assign`, {
      method: "POST",
      body: JSON.stringify({ owner }),
    }),
  incidentStatus: (id: string, status: IncidentStatus) =>
    request<Incident>(`/incidents/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status }),
    }),
  incidentExport: (id: string) => request<Record<string, unknown>>(`/incidents/${id}/export`),

  threatIntel: () =>
    request<{
      feed: ThreatAdvisory[];
      sources: string[];
      stats: { total: number; active: number; critical: number; avgCvss: number };
      lastSynced: string;
    }>("/threat-intel"),
  presence: () => request<AnalystPresence[]>("/presence"),

  executive: () => request<ExecutiveStats>("/executive"),
  soc: () => request<SocStats>("/soc"),
  twin: () => request<TwinStats>("/twin"),
  analytics: () => request<AnalyticsStats>("/analytics"),
  explain: () => request<ExplainStats>("/explain"),
  system: () => request<SystemStats>("/system"),
  systemDatabase: () => request<{
    postgresql: { available: boolean; mode: string };
    mongodb: { available: boolean; latencyMs?: number; error?: string; collections: string[] };
    timestamp: string;
  }>("/system/database"),
  systemCache: () => request<{
    redis: { available: boolean; latencyMs?: number; error?: string; hitRatio: number; keysCount: number; memoryUsed: string };
    timestamp: string;
  }>("/system/cache"),
  systemConnections: () => request<{
    database: { active: number; idle: number; max: number };
    redis: { connected: boolean; subscribers: number };
    websocket: { active: number };
    timestamp: string;
  }>("/system/connections"),

  llmStatus: () => request<LLMStatus>("/llm/status"),
  llmUsage: () =>
    request<{
      usage: { promptTokens: number; completionTokens: number; totalTokens: number; estimatedCostUsd: number; requests: number; simulated: boolean };
      provider: string;
      timestamp: string;
    }>("/llm/usage"),
  executiveInsights: () => request<AIResponse<ExecutiveInsight[]>>("/executive/insights"),
  policyRecommend: (industry?: string, enabledPacks?: string[]) =>
    request<AIResponse<PolicyRecommendation[]>>("/policies/recommend", {
      method: "POST",
      body: JSON.stringify({ industry, enabledPacks }),
    }),
  complianceSummary: () => request<AIResponse<string>>("/compliance/summary"),
  aiReasoning: (id: string) => request<AIResponse<string>>(`/explain/${id}/ai-reasoning`),
  copilotIntent: (message: string) =>
    request<AIResponse<string>>("/copilot/intent", {
      method: "POST",
      body: JSON.stringify({ message }),
    }),

  // Health & System
  health: (service: string) => request<any>(`/health/${service}`),

  // Billing & Subscription
  createOrder: (planId: string, billingCycle: string) =>
    request<{ order: any; plan: any; amount: number }>("/billing/create-order", {
      method: "POST",
      body: JSON.stringify({ planId, billingCycle }),
    }),
  verifyPayment: (razorpay_order_id: string, razorpay_payment_id: string, razorpay_signature: string) =>
    request<{ success: boolean; subscription?: any }>("/billing/verify-payment", {
      method: "POST",
      body: JSON.stringify({ razorpay_order_id, razorpay_payment_id, razorpay_signature }),
    }),
  subscription: () => request<any>("/billing/subscription"),
  invoices: () => request<{ invoices: any[] }>("/billing/invoices"),
  billingUsage: () => request<any>("/billing/usage"),
  billingAnalytics: () => request<any>("/billing/analytics"),

  // Employee API Key Management
  listMyApiKeys: () => request<any[]>("/me/api-keys"),
  createApiKey: (name: string) =>
    request<{ success: boolean; apiKey: { id: string; name: string; prefix: string; secret: string; createdAt: string; warning: string } }>("/admin/api-keys", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  listAdminApiKeys: (organizationId?: string) =>
    request<any[]>(`/admin/api-keys${organizationId ? `?organizationId=${organizationId}` : ""}`),
  revokeApiKey: (id: string) =>
    request<{ success: boolean }>(`/admin/api-keys/${id}/revoke`, { method: "POST" }),
  rotateApiKey: (id: string) =>
    request<{ success: boolean; apiKey: { id: string; name: string; prefix: string; secret: string; createdAt: string; warning: string } }>(`/admin/api-keys/${id}/rotate`, { method: "POST" }),
};

export const PROVIDERS = [
  { id: "openai", label: "OpenAI", model: "gpt-4o-mini" },
  { id: "gemini", label: "Google Gemini", model: "gemini-1.5-flash" },
  { id: "claude", label: "Anthropic Claude", model: "claude-3-5-haiku" },
  { id: "ollama", label: "Ollama (local)", model: "llama3.1" },
  { id: "openrouter", label: "OpenRouter", model: "gpt-4o-mini" },
] as const;

export const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "text-status-critical",
  HIGH: "text-status-high",
  MEDIUM: "text-status-medium",
  LOW: "text-status-low",
  INFO: "text-status-info",
};

export const SEVERITY_BG: Record<string, string> = {
  CRITICAL: "bg-critical",
  HIGH: "bg-high",
  MEDIUM: "bg-medium",
  LOW: "bg-low",
  INFO: "bg-info",
};

export const DECISION_COLORS: Record<string, string> = {
  BLOCK: "bg-status-critical",
  REWRITE: "bg-status-high",
  FLAG: "bg-status-medium",
  ALLOW: "bg-status-low",
  REVIEW: "bg-status-info",
};

export const THREAT_COLORS: Record<string, string> = {
  CRITICAL: "text-status-critical",
  HIGH: "text-status-high",
  MEDIUM: "text-status-medium",
  LOW: "text-status-low",
  SAFE: "text-status-low",
};

export const PALETTE = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#f59e0b",
  low: "#10b981",
  info: "#3b82f6",
  accent: "#0f766e",
  accentLight: "#14b8a6",
  accentDark: "#0d5c56",
  muted: "#71717a",
  border: "#27272a",
  bgCard: "#18181b",
  bgElevated: "#1f1f23",
} as const;

export function threatLevelFromScore(score: number): "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE" {
  if (score >= 80) return "CRITICAL";
  if (score >= 60) return "HIGH";
  if (score >= 35) return "MEDIUM";
  if (score >= 15) return "LOW";
  return "SAFE";
}

export function formatTime(ts: string | Date): string {
  return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function formatDate(ts: string | Date): string {
  return new Date(ts).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" });
}

export function timeAgo(ts: string | Date): string {
  const s = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (s < 5) return "just now";
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}