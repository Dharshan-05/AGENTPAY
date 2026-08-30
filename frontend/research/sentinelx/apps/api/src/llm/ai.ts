import { complete, completeJson, isProviderConfigured, listProviderStatus, type ChatMessage } from './providers';
import { estimateTextTokens } from './tokens';

export interface AIResult<T> {
  result: T;
  model: string | null;
  tokensUsed: number;
  latencyMs: number;
  simulated: boolean;
}

const DEFAULT_PROVIDER = process.env.DEFAULT_LLM_PROVIDER ?? 'openrouter';

export function pickProvider(): string {
  const order = [DEFAULT_PROVIDER, 'openrouter', 'openai', 'claude', 'gemini', 'ollama'];
  for (const p of order) {
    if (isProviderConfigured(p)) return p;
  }
  return 'openrouter';
}

const SIMULATED_FALLBACK =
  process.env.LLM_SIMULATED_MODE !== '0';

function system(role: string): ChatMessage {
  return { role: 'system', content: role };
}

async function runAI<T>(
  build: () => Promise<T>,
  fallback: () => T,
): Promise<AIResult<T>> {
  const provider = pickProvider();
  const startedAt = performance.now();
  if (!isProviderConfigured(provider)) {
    return {
      result: fallback(),
      model: null,
      tokensUsed: 0,
      latencyMs: 0,
      simulated: true,
    };
  }
  try {
    const out = await build();
    return {
      result: out,
      model: provider,
      tokensUsed: 0,
      latencyMs: Math.round(performance.now() - startedAt),
      simulated: false,
    };
  } catch (err) {
    return {
      result: SIMULATED_FALLBACK ? fallback() : (() => { throw err })(),
      model: provider,
      tokensUsed: 0,
      latencyMs: Math.round(performance.now() - startedAt),
      simulated: true,
    };
  }
}

export interface ExecutiveInsight {
  id: string;
  category: 'risk' | 'trend' | 'compliance' | 'recommendation' | 'kpi';
  title: string;
  summary: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'positive';
  metric?: { label: string; value: string; delta?: string };
}

export async function generateExecutiveInsights(
  context: { score: number; blocked: number; rewritten: number; critical: number; deptRisk: { dept: string; risk: number }[] },
): Promise<AIResult<ExecutiveInsight[]>> {
  const fallback = (): ExecutiveInsight[] => [
    {
      id: 'i1',
      category: 'kpi',
      title: 'Security posture is solid',
      summary: `Company security score stands at ${context.score}/100 with ${context.blocked} threats blocked this period.`,
      severity: 'positive',
      metric: { label: 'Security score', value: `${context.score}/100` },
    },
    {
      id: 'i2',
      category: 'risk',
      title: `${context.critical} critical events intercepted`,
      summary: 'Critical threats were detected and blocked before reaching the model provider. No data left the perimeter.',
      severity: 'high',
    },
    ...context.deptRisk.slice(0, 2).map((d, i) => ({
      id: `i3-${i}`,
      category: 'trend' as const,
      title: `${d.dept} is a risk hotspot`,
      summary: `Department risk index of ${d.risk}% places ${d.dept} above the organization baseline. Recommend targeted security training.`,
      severity: (d.risk >= 60 ? 'critical' : 'medium') as 'critical' | 'medium',
      metric: { label: 'Risk index', value: `${d.risk}%` },
    })),
    {
      id: 'i4',
      category: 'recommendation',
      title: 'Continue monitoring',
      summary: 'Posture is stable. Maintain current policy packs and re-run the monthly compliance review.',
      severity: 'low',
    },
  ];

  return runAI(
    async () => {
      const messages: ChatMessage[] = [
        system(
          'You are the SentinelX executive security analyst. Given the security telemetry, produce 3-6 concise, specific executive insights. Return a JSON array with objects: { id, category (risk|trend|compliance|recommendation|kpi), title, summary, severity (critical|high|medium|low|positive), metric?: { label, value, delta? } }. Be concrete and data-driven.',
        ),
        { role: 'user', content: JSON.stringify(context) },
      ];
      const res = await completeJson<ExecutiveInsight[]>({
        provider: pickProvider(),
        model: 'auto',
        messages,
        temperature: 0.4,
      });
      return Array.isArray(res) ? res : fallback();
    },
    fallback,
  );
}

export interface PolicyRecommendation {
  id: string;
  pack: string;
  regulation: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  rationale: string;
  action: string;
}

export async function recommendPolicies(
  context: { industry: string; recentViolations: { regulation: string; count: number }[]; enabledPacks: string[] },
): Promise<AIResult<PolicyRecommendation[]>> {
  const fallback = (): PolicyRecommendation[] => {
    const recs: PolicyRecommendation[] = [];
    const needs = new Map<string, number>();
    for (const v of context.recentViolations) needs.set(v.regulation, v.count);
    const priorities: Record<string, 'critical' | 'high' | 'medium' | 'low'> = {
      'PCI DSS': 'critical',
      GDPR: 'high',
      HIPAA: 'high',
      'SOC 2': 'medium',
      'ISO 27001': 'medium',
    };
    for (const [reg, count] of needs) {
      if (context.enabledPacks.includes(reg)) continue;
      recs.push({
        id: `p-${reg.toLowerCase().replace(/[^a-z0-9]/g, '-')}`,
        pack: `${reg} Policy Pack`,
        regulation: reg,
        priority: priorities[reg] ?? 'medium',
        rationale: `${count} recent violations reference ${reg} requirements.`,
        action: `Enable the ${reg} pack to enforce these controls automatically.`,
      });
    }
    if (recs.length === 0) {
      recs.push({
        id: 'p-industry',
        pack: `${context.industry} Baseline Pack`,
        regulation: context.industry,
        priority: 'low',
        rationale: 'No uncovered violations detected.',
        action: 'Maintain current packs; review quarterly.',
      });
    }
    return recs;
  };

  return runAI(
    async () => {
      const messages: ChatMessage[] = [
        system(
          'You are a security compliance advisor. Recommend policy packs for an AI governance platform. Return a JSON array of { id, pack, regulation, priority (critical|high|medium|low), rationale, action }. Be specific about the regulation.',
        ),
        { role: 'user', content: JSON.stringify(context) },
      ];
      const res = await completeJson<PolicyRecommendation[]>({
        provider: pickProvider(),
        model: 'auto',
        messages,
        temperature: 0.4,
      });
      return Array.isArray(res) ? res : fallback();
    },
    fallback,
  );
}

export async function generateComplianceSummary(
  context: { regulation: string; count: number; policies: string[]; departments: string[] }[],
): Promise<AIResult<string>> {
  const fallback = (): string => {
    if (context.length === 0) {
      return 'No compliance violations were recorded in the last 7 days across GDPR, HIPAA, PCI DSS, SOC 2 and ISO 27001. The organization is operating with a clean compliance posture.';
    }
    const lines = context.map(
      (c) =>
        `- **${c.regulation}**: ${c.count} violation(s) across ${[...new Set(c.departments)].join(', ') || 'multiple teams'}. Involved controls: ${[...new Set(c.policies)].join(', ') || 'n/a'}.`,
    );
    const top = [...context].sort((a, b) => b.count - a.count)[0];
    return `**Compliance snapshot (7 days):**\n\n${lines.join('\n')}\n\n**Priority focus:** ${top.regulation} shows the most activity (${top.count} events). Recommend immediate review and tightened enforcement.`;
  };

  return runAI(
    async () => {
      const messages: ChatMessage[] = [
        system(
          'You are a compliance officer summarizing security violations for executives. Return 3-6 short, professional markdown paragraphs grounded ONLY in the provided data. Do not invent metrics.',
        ),
        { role: 'user', content: JSON.stringify(context) },
      ];
      const res = await complete({
        provider: pickProvider(),
        model: 'auto',
        messages,
        temperature: 0.4,
        maxTokens: 500,
      });
      return res.text || fallback();
    },
    fallback,
  );
}

export async function explainDecisionAI(
  context: { prompt: string; decision: string; riskScore: number; threatLevel: string; violations: string[]; riskFactors: { label: string; weight: number }[] },
): Promise<AIResult<string>> {
  const fallback = (): string => {
    const top = context.riskFactors.sort((a, b) => b.weight - a.weight)[0];
    return [
      `**Why this decision was made:**`,
      ``,
      `The prompt was evaluated by the SentinelX governance pipeline and assigned a risk score of **${context.riskScore}/100 (${context.threatLevel})**, resulting in a **${context.decision}** decision.`,
      ``,
      `Primary risk driver: **${top?.label ?? 'no single dominant factor'}** (weight ${top?.weight ?? 0}).`,
      context.violations.length > 0 ? `Policy context: ${context.violations.slice(0, 3).map((v) => `**${v}**`).join(', ')}.` : 'No policy packs were triggered.',
      ``,
      context.decision === 'BLOCK'
        ? 'Because the risk score exceeded the block threshold, the prompt was never transmitted to the model provider and an incident was raised for investigation.'
        : context.decision === 'REWRITE'
          ? 'Sensitive entities were redacted before transmission so the model could still answer without exposing data.'
          : 'The request was considered safe enough to allow, with monitoring continued.',
    ].join('\n');
  };

  return runAI(
    async () => {
      const messages: ChatMessage[] = [
        system(
          'You are the SentinelX explainability agent. Explain this security decision in 2-4 short professional paragraphs. Be specific about the risk drivers and what happens next. Use the data provided; do not invent metrics.',
        ),
        { role: 'user', content: JSON.stringify(context) },
      ];
      const res = await complete({
        provider: pickProvider(),
        model: 'auto',
        messages,
        temperature: 0.3,
        maxTokens: 400,
      });
      return res.text || fallback();
    },
    fallback,
  );
}

export async function rewritePromptAI(
  context: { original: string; secrets: { label: string; value: string }[] },
): Promise<AIResult<string>> {
  const fallback = (): string => {
    let out = context.original;
    for (const s of context.secrets) {
      out = out.replaceAll(s.value, `[REDACTED ${s.label.toUpperCase()}]`);
    }
    return out;
  };

  return runAI(
    async () => {
      const messages: ChatMessage[] = [
        system(
          'You are a data-privacy rewriter. Rewrite the given prompt to remove sensitive data (replace exact secret values with [REDACTED <TYPE>]) while preserving the user\'s intent and structure. Return ONLY the rewritten prompt, no commentary.',
        ),
        { role: 'user', content: JSON.stringify(context) },
      ];
      const res = await complete({
        provider: pickProvider(),
        model: 'auto',
        messages,
        temperature: 0.1,
        maxTokens: 400,
      });
      return res.text || fallback();
    },
    fallback,
  );
}

export async function classifyIntentAI(message: string): Promise<AIResult<string>> {
  const fallback = (): string => 'generic';
  return runAI(
    async () => {
      const messages: ChatMessage[] = [
        system(
          'Classify the user request into exactly one of these intents: blocked_prompt, high_risk_prompts, policy_triggers, rewriting, weekly_violations, detection_categories, recommendations, department_risk, why_threats, compare_days, today_trend, compliance, executive_summary, generic. Reply with ONLY the intent id, no punctuation.',
        ),
        { role: 'user', content: message },
      ];
      const res = await complete({ provider: pickProvider(), model: 'auto', messages, temperature: 0, maxTokens: 12 });
      const intent = res.text.trim().toLowerCase().replace(/[^a-z_]/g, '');
      return intent || fallback();
    },
    fallback,
  );
}

export function getProviderStatus() {
  return { providers: listProviderStatus(), defaultProvider: pickProvider() };
}

export async function summarizeWithTokens(text: string): Promise<number> {
  return estimateTextTokens(text);
}
