import 'dotenv/config';
import Fastify from 'fastify';
import cors from '@fastify/cors';
import cookie from '@fastify/cookie';
import helmet from '@fastify/helmet';
import { Server } from 'socket.io';
import { SentinelPipeline } from './agents/pipeline';
import { seedDemoDataIfEmpty } from './lib/redis';
import { store } from './lib/store';
import { registerEnterpriseRoutes } from './routes/enterprise';
import { registerAIRoutes } from './routes/ai';
import { complete, isProviderConfigured } from './llm/providers';
import { pickProvider } from './llm/ai';
import type { ChatMessage } from './llm/providers';
import { createIncidentFromScan } from './lib/incidents';
import { getPresence, registerAnalyst, unregisterAnalyst } from './lib/presence';
import { registerIncidentRoutes } from './routes/incidents';
import { registerThreatIntelRoutes } from './routes/threat-intel';
import { validateEnv } from './lib/env';
import './lib/prisma';
import { listProviderStatus } from './llm/providers';
import { registerAuthRoutes } from './routes/auth';
import { verifyToken } from './lib/auth';
import { registerOpenRouterRoutes } from './routes/openrouter';
import { registerApiKeyRoutes } from './routes/api-keys';
import { registerGatewayRoutes } from './routes/gateway';
import { registerGovernanceRoutes } from './routes/governance';
import { registerAnalyticsRoutes } from './routes/analytics';

function system(role: string): ChatMessage {
  return { role: 'system', content: role };
}

const PORT = Number(process.env.PORT) || 8080;

const envReport = validateEnv();

export const fastify = Fastify({
  logger: process.env.NODE_ENV !== 'test' ? {
    level: 'info',
    transport: undefined,
    redact: {
      paths: ['req.headers.authorization', 'req.headers.cookie', 'req.headers["x-api-key"]'],
      censor: '[REDACTED]',
    },
  } : false,
});

const ALLOWED_ORIGINS = [
  'https://sentinelx.ai',
  'https://web-nine-dun-97.vercel.app',
  'https://sentinel--ai.vercel.app',
  'http://localhost:3000',
  'http://localhost:3001',
  ...(process.env.WEB_ORIGIN
    ? process.env.WEB_ORIGIN.split(',').map((o) => o.trim()).filter(Boolean)
    : []),
];

await fastify.register(cors, {
  origin: (origin, cb) => {
    // Allow requests with no origin (e.g. curl, Railway healthcheck, server-to-server)
    if (!origin || ALLOWED_ORIGINS.includes(origin)) {
      cb(null, true);
    } else {
      fastify.log.warn(`[cors] Blocked origin: ${origin}`);
      cb(new Error('Not allowed by CORS'), false);
    }
  },
  credentials: true,
});

await fastify.register(cookie);

await fastify.register(helmet, {
  contentSecurityPolicy: false,
});

await fastify.register(import('@fastify/rate-limit'), {
  max: 300,
  timeWindow: '1 minute',
});

const io = new Server(fastify.server, {
  cors: { origin: ALLOWED_ORIGINS, credentials: true },
});

io.use((socket, next) => {
  const token =
    (socket.handshake.auth?.token as string | undefined) ||
    (socket.handshake.query?.token as string | undefined);
  if (!token) {
    return next(new Error('Authentication required'));
  }
  const payload = verifyToken(token);
  if (!payload) {
    return next(new Error('Invalid or expired token'));
  }
  (socket as any).user = payload;
  next();
});

io.on('connection', (socket) => {
  socket.emit('hello', { service: 'sentinelx', version: '1.0.0' });
  const analystId = (socket.handshake.query?.analyst as string | undefined) ?? 'an-1';
  registerAnalyst(socket.id, analystId);
  io.emit('presence:update', getPresence());
  socket.on('disconnect', () => {
    unregisterAnalyst(socket.id);
    io.emit('presence:update', getPresence());
  });
});

export function emitAgentEvent(trace: unknown) {
  io.emit('agent:update', trace);
}

export function emitScanEvent(result: unknown) {
  io.emit('scan:complete', result);
}

const pipeline = new SentinelPipeline((trace) => emitAgentEvent(trace));

seedDemoDataIfEmpty().catch((err) => {
  fastify.log.error({ err }, 'Seed failed, continuing without demo data');
});

await registerEnterpriseRoutes(fastify);
await registerAIRoutes(fastify);
await registerIncidentRoutes(fastify);
await registerThreatIntelRoutes(fastify);
await registerAuthRoutes(fastify);
await registerApiKeyRoutes(fastify);
await registerGatewayRoutes(fastify);
await registerOpenRouterRoutes(fastify);
await registerGovernanceRoutes(fastify);
await registerAnalyticsRoutes(fastify);

fastify.get('/api/presence', async () => getPresence());

fastify.get('/', async () => {
  return {
    service: 'SentinelX API',
    status: 'ok',
    version: '1.0.0',
    health: '/api/health',
  };
});

fastify.get('/api/health', async () => {
  const providers = listProviderStatus();
  return {
    status: 'ok',
    service: 'sentinelx-api',
    version: '1.0.0',
    uptimeSeconds: Math.round(process.uptime()),
    timestamp: new Date().toISOString(),
    providers: providers.map((p) => ({ id: p.id, configured: p.configured })),
  };
});

fastify.get('/api/health/dependencies', async () => {
  // Try to connect to Redis
  let redisStatus = 'not_configured';
  try {
    const redisModule = await import('./lib/redis');
    redisStatus = redisModule.getRedis().status === 'ready' ? 'healthy' : 'degraded';
  } catch {
    redisStatus = 'unavailable';
  }

  // Database status (Prisma)
  let dbStatus = 'not_configured';
  try {
    const { dbAvailable } = await import('./lib/prisma');
    const available = await dbAvailable();
    dbStatus = available ? 'healthy' : 'degraded (in-memory demo mode)';
  } catch {
    dbStatus = 'unavailable';
  }

  return {
    status: 'healthy',
    api: 'healthy',
    dependencies: {
      mongodb: 'not_configured', // using Postgres/Prisma instead
      postgresql: dbStatus,
      redis: redisStatus,
      openrouter: listProviderStatus().find(p => p.id === 'openrouter')?.configured ? 'healthy' : 'not_configured',
      razorpay: process.env.RAZORPAY_KEY_ID ? 'healthy' : 'not_configured',
      cloudinary: 'not_configured',
      websocket: 'healthy' // Socket.io is bound to the Fastify instance
    }
  };
});


fastify.post('/api/scan', async (request, reply) => {
  const body = request.body as {
    prompt: string;
    userId?: string;
    provider?: string;
    model?: string;
  };

  if (!body?.prompt?.trim()) {
    return reply.code(400).send({ error: 'Prompt is required' });
  }

  if (body.prompt.length > 50_000) {
    return reply.code(413).send({ error: 'Prompt exceeds 50,000 characters' });
  }

  const result = await pipeline.execute(body.prompt, {
    userId: body.userId,
    provider: body.provider ?? 'openai',
    model: body.model ?? 'auto',
    ipAddress: request.ip,
  });

  emitScanEvent({ auditLogId: result.auditLogId, decision: result.decision, riskScore: result.riskScore });

  const incident = createIncidentFromScan({
    decision: result.decision,
    riskScore: result.riskScore,
    prompt: result.originalPrompt,
    violations: result.violations as Array<{ policyName: string }>,
  });
  if (incident) io.emit('incident:new', incident);

  return reply.send(result);
});

fastify.get('/api/dashboard', async () => {
  const now = Date.now();
  const dayAgo = now - 24 * 3600 * 1000;
  const weekAgo = now - 7 * 24 * 3600 * 1000;

  const [totalPrompts, blocked, recent, violations24h, sessions, allRecords, recent24h, recent7d] = await Promise.all([
    store.auditLog.count(),
    store.auditLog.count({ where: { decision: { in: ['BLOCK', 'REWRITE', 'FLAG'] } } }),
    store.auditLog.findMany({ orderBy: { timestamp: 'desc' }, take: 50 }),
    store.auditLog.count({
      where: { timestamp: { gte: new Date(dayAgo) }, riskScore: { gte: 35 } },
    }),
    store.session.count({ where: { active: true } }),
    store.auditLog.findMany({ orderBy: { timestamp: 'desc' }, take: 500 }),
    store.auditLog.findMany({ where: { timestamp: { gte: new Date(dayAgo) } }, orderBy: { timestamp: 'desc' }, take: 200 }),
    store.auditLog.findMany({ where: { timestamp: { gte: new Date(weekAgo) } }, orderBy: { timestamp: 'desc' }, take: 500 }),
  ]) as [
    number,
    number,
    Array<{
      id: string;
      prompt: string;
      promptHash: string;
      riskScore: number;
      riskScoreNum?: number;
      secrets: unknown;
      violations: unknown;
      rewrittenPrompt: string | null;
      threatLevel: string;
      decision: string;
      timestamp: Date | string;
      llmProvider: string | null;
      userId: string | null;
      user: { id: string; name: string; email: string; department: string } | null;
    }>,
    number,
    number,
    Array<any>,
    Array<any>,
    Array<any>,
  ];

  const avgRisk = recent.reduce((acc, r) => acc + Number(r.riskScore ?? 0), 0) / Math.max(recent.length, 1);
  const riskDistribution = { low: 0, medium: 0, high: 0, critical: 0 };
  const topCategories = new Map<string, number>();
  const departmentRisk = new Map<string, { total: number; risky: number; scoreSum: number }>();
  const hourlyAttacks = new Map<number, number>();
  const dailyAttacks = new Map<string, number>();
  const policyViolations = new Map<string, { count: number; regulation: string; severity: string }>();
  const secretTypes = new Map<string, number>();
  let totalLatency = 0;
  let latencyCount = 0;
  let detectionHits = 0;
  let detectionTotal = 0;

  for (const r of allRecords) {
    const score = Number(r.riskScore ?? 0);
    if (score >= 80) riskDistribution.critical++;
    else if (score >= 60) riskDistribution.high++;
    else if (score >= 35) riskDistribution.medium++;
    else riskDistribution.low++;

    const secrets = (r.secrets ?? []) as Array<{ label: string }>;
    for (const s of secrets) {
      topCategories.set(s.label, (topCategories.get(s.label) ?? 0) + 1);
      secretTypes.set(s.label, (secretTypes.get(s.label) ?? 0) + 1);
      detectionHits++;
    }
    detectionTotal += secrets.length > 0 ? 1 : 0;

    const ts = new Date(String(r.timestamp)).getTime();
    const hour = new Date(ts).getHours();
    hourlyAttacks.set(hour, (hourlyAttacks.get(hour) ?? 0) + (score >= 35 ? 1 : 0));

    const dayKey = new Date(ts).toISOString().split('T')[0];
    dailyAttacks.set(dayKey, (dailyAttacks.get(dayKey) ?? 0) + (score >= 35 ? 1 : 0));

    const user = r.user;
    if (user?.department) {
      const dept = departmentRisk.get(user.department) ?? { total: 0, risky: 0, scoreSum: 0 };
      dept.total++;
      dept.scoreSum += score;
      if (score >= 35) dept.risky++;
      departmentRisk.set(user.department, dept);
    }

    const violations = (r.violations ?? []) as Array<{ policyName: string; regulation: string; severity: string }>;
    for (const v of violations) {
      const key = v.policyName;
      const entry = policyViolations.get(key) ?? { count: 0, regulation: v.regulation, severity: v.severity };
      entry.count++;
      policyViolations.set(key, entry);
    }

    if (r.latencyMs) {
      totalLatency += Number(r.latencyMs);
      latencyCount++;
    }
  }

  const safeRequests = Math.max(0, totalPrompts - blocked);
  const detectionAccuracy = detectionTotal > 0 ? Math.round((detectionHits / detectionTotal) * 100) : 99;
  const avgResponseTime = latencyCount > 0 ? Math.round(totalLatency / latencyCount) : 45;

  const topViolatedPolicies = [...policyViolations.entries()]
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 5)
    .map(([policyName, v]) => ({ policyName, count: v.count, regulation: v.regulation, severity: v.severity }));

  const departmentRiskArray = [...departmentRisk.entries()]
    .map(([department, v]) => ({
      department,
      riskIndex: v.total > 0 ? Math.round((v.risky / v.total) * 100) : 0,
      avgScore: v.total > 0 ? Math.round(v.scoreSum / v.total) : 0,
      totalPrompts: v.total,
    }))
    .sort((a, b) => b.riskIndex - a.riskIndex)
    .slice(0, 5);

  const hourlyTrend = Array.from({ length: 24 }, (_, h) => ({
    hour: h,
    attacks: hourlyAttacks.get(h) ?? 0,
  }));

  const weeklyTrend = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(now - (6 - i) * 24 * 3600 * 1000);
    const key = d.toISOString().split('T')[0];
    return {
      day: d.toLocaleDateString([], { weekday: 'short' }),
      attacks: dailyAttacks.get(key) ?? 0,
    };
  });

  const topSecretTypes = [...secretTypes.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([type, count]) => ({ type, count }));

  const activeIncidents = recent24h.filter((r) => Number(r.riskScore ?? 0) >= 60).length;
  const criticalIncidents = recent24h.filter((r) => Number(r.riskScore ?? 0) >= 80).length;
  const complianceHealth = Math.max(0, 100 - Math.round((violations24h / Math.max(totalPrompts, 1)) * 1000));

  return {
    totalPrompts,
    blockedPrompts: blocked,
    safeRequests,
    riskScore: Math.round(avgRisk),
    activeSessions: sessions,
    violations24h,
    agentsOnline: 8,
    activeIncidents,
    criticalIncidents,
    complianceHealth,
    detectionAccuracy,
    avgResponseTime,
    promptsTrend: recent.slice(0, 12).reverse().map((r) => Number(r.riskScore ?? 0)),
    riskDistribution,
    topCategories: [...topCategories.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([category, count]) => ({ category, count })),
    topViolatedPolicies,
    departmentRisk: departmentRiskArray,
    hourlyTrend,
    weeklyTrend,
    topSecretTypes,
    securityTrend: recent7d.slice(0, 30).reverse().map((r) => Number(r.riskScore ?? 0)),
    recentEvents: recent.map((r) => ({
      id: r.id,
      promptHash: r.promptHash,
      prompt: r.prompt.slice(0, 200),
      rewrittenPrompt: r.rewrittenPrompt,
      violations: r.violations,
      riskScore: Number(r.riskScore ?? 0),
      threatLevel: r.threatLevel,
      decision: r.decision,
      timestamp: new Date(String(r.timestamp)).toISOString(),
      user: r.user ? { id: r.user.id, name: r.user.name, email: r.user.email, department: r.user.department } : null,
      llmProvider: r.llmProvider,
    })),
  };
});

fastify.get('/api/audit', async (request) => {
  const query = request.query as { page?: string; limit?: string; search?: string };
  const page = Math.max(1, Number(query.page ?? 1));
  const limit = Math.min(50, Math.max(1, Number(query.limit ?? 20)));
  const search = query.search?.trim();

  const where = search
    ? {
        OR: [
          { prompt: { contains: search, mode: 'insensitive' as const } },
          { promptHash: { contains: search } },
        ],
      }
    : {};

  const [total, records] = await Promise.all([
    store.auditLog.count({ where }),
    store.auditLog.findMany({
      where,
      orderBy: { timestamp: 'desc' },
      skip: (page - 1) * limit,
      take: limit,
      include: { user: true },
    }),
  ]);

  return { total, page, limit, records };
});

fastify.get('/api/audit/:id', async (request, reply) => {
  const { id } = request.params as { id: string };
  const record = await store.auditLog.findUnique({ where: { id } });
  if (!record) return reply.code(404).send({ error: 'Audit record not found' });
  return record;
});

fastify.get('/api/policies', async () => {
  const policies = await store.policy.findMany();
  return policies;
});

fastify.get('/api/rules', async () => {
  const rules = await store.detectionRule.findMany();
  return rules;
});

fastify.get('/api/alerts', async () => {
  return store.alert.findMany({ take: 50 });
});

fastify.post('/api/alerts/:id/ack', async (request) => {
  const { id } = request.params as { id: string };
  return store.alert.update({ where: { id }, data: { acknowledged: true } });
});

fastify.get('/api/settings', async () => {
  const settings = await store.setting.findMany();
  const map: Record<string, string> = {};
  for (const s of settings) map[s.key] = s.value;
  return map;
});

fastify.get('/api/agents/health', async () => {
  const agents = [
    { id: 'inspector-agent', name: 'Inspector Agent', responsibility: 'Prompt classification & intent analysis', latency: 3, processed: 1842, success: 99.8, memory: 84, task: 'Parsing inbound prompt structure' },
    { id: 'secret-detection-agent', name: 'Secret Detection Agent', responsibility: '30+ deterministic pattern rules', latency: 2, processed: 1842, success: 99.4, memory: 128, task: 'Scanning for credentials & PII' },
    { id: 'policy-engine', name: 'Policy Engine', responsibility: 'GDPR / HIPAA / PCI DSS / SOC 2 / ISO 27001', latency: 1, processed: 1183, success: 99.9, memory: 96, task: 'Evaluating 7 policy packs' },
    { id: 'risk-engine', name: 'Risk Engine', responsibility: 'Live enterprise risk scoring', latency: 4, processed: 1842, success: 99.7, memory: 72, task: 'Scoring composite risk' },
    { id: 'prompt-rewriter', name: 'Prompt Rewriter', responsibility: 'Intent-preserving sanitisation', latency: 2, processed: 417, success: 98.9, memory: 64, task: 'Redacting sensitive entities' },
    { id: 'llm-adapter', name: 'LLM Adapter', responsibility: 'Multi-provider gateway routing', latency: 8, processed: 1604, success: 99.2, memory: 152, task: 'Streaming model response' },
    { id: 'audit-logger', name: 'Audit Logger', responsibility: 'Tamper-evident audit trail', latency: 3, processed: 1842, success: 100, memory: 48, task: 'Committing audit record' },
    { id: 'memory-agent', name: 'Memory Agent', responsibility: 'Session context & behavioural signals', latency: 1, processed: 1842, success: 99.9, memory: 88, task: 'Updating session profile' },
  ];
  const tasks = [...agents];
  const tick = Math.floor(Date.now() / 8000) % tasks.length;
  return agents.map((a, i) => ({
    id: a.id,
    name: a.name,
    responsibility: a.responsibility,
    status: 'HEALTHY',
    lastPing: new Date().toISOString(),
    responseTime: Math.round(a.latency + Math.random() * 4),
    processed: a.processed + Math.floor(Math.random() * 4),
    successRate: a.success,
    memoryMb: a.memory,
    currentTask: i === tick ? a.task : i === (tick + 1) % tasks.length ? a.task : 'Idle · awaiting pipeline',
  }));
});

fastify.get('/api/copilot/suggestions', async () => [
  { id: 's1', text: 'Why was the last prompt blocked?' },
  { id: 's2', text: "Show today's highest-risk prompts" },
  { id: 's3', text: 'Which policy triggered most violations this week?' },
  { id: 's4', text: 'What changed after rewriting?' },
  { id: 's5', text: 'How many violations occurred this week?' },
  { id: 's6', text: 'Which detection category is most common?' },
  { id: 's7', text: 'Recommend improvements for our security posture' },
  { id: 's8', text: 'Which department has the highest risk?' },
  { id: 's9', text: 'Summarise today\'s security trend' },
  { id: 's10', text: 'Why did threats increase this week?' },
  { id: 's11', text: 'Compare today vs yesterday' },
  { id: 's12', text: 'Show GDPR violations' },
  { id: 's13', text: 'Explain the current security posture' },
  { id: 's14', text: 'Generate an executive summary' },
]);

fastify.post('/api/copilot', async (request) => {
  const { message, history, sessionId } = request.body as { message: string; history?: Array<{ role: string; content: string }>; sessionId?: string };
  const session = sessionId ?? 'demo-session';
  const prior = copilotMemory.get(session) ?? [];
  const pastUser = [...prior, ...(history ?? [])].filter((m) => m.role === 'user').map((m) => m.content).slice(-6);
  const ruleAnswer = await answerCopilot(message, pastUser);
  const enhanced = await answerCopilotAI(message, ruleAnswer, prior);
  prior.push({ role: 'user', content: message });
  prior.push({ role: 'assistant', content: ruleAnswer.answer });
  copilotMemory.set(session, prior.slice(-40));
  const recalled = recallTopic(message, pastUser);
  return { ...enhanced, memory: { count: pastUser.length, recalled } };
});

const copilotMemory = new Map<string, Array<{ role: 'user' | 'assistant'; content: string }>>();

const DEPARTMENT_NAMES = ['finance', 'engineering', 'human resources', 'hr', 'legal', 'sales', 'marketing', 'operations', 'support'];

function recallTopic(message: string, history: string[]): string | null {
  const lower = message.toLowerCase();
  const hasRef = /(it|that|this|they|them|those|same|previous|last time|earlier|before|then)/.test(lower);
  const isFollowup = /(compare|how|why|what|continue|more|again|details|specifically|further|explain)/.test(lower);
  if (!hasRef && !isFollowup) return null;
  for (let i = history.length - 1; i >= 0; i--) {
    const h = history[i].toLowerCase();
    const dept = DEPARTMENT_NAMES.find((d) => h.includes(d));
    if (dept) return dept === 'hr' ? 'Human Resources' : dept.charAt(0).toUpperCase() + dept.slice(1);
    if (/(policy|policy|violation|gdpr|hipaa|pci|secret|credential|leak|incident)/.test(h)) return 'recent policy activity';
  }
  return null;
}

async function answerCopilotAI(message: string, ruleAnswer: { answer: string; data?: unknown }, history: Array<{ role: 'user' | 'assistant'; content: string }> = []): Promise<{ answer: string; data?: unknown; model?: string; tokensUsed?: number; simulated?: boolean }> {
  const provider = pickProvider();
  if (!isProviderConfigured(provider)) return ruleAnswer;
  try {
    const messages: ChatMessage[] = [
      system(
        'You are the SentinelX executive security copilot. The user asked a question, and we have an accurate data-derived answer with structured data. Rephrase and enrich the answer in a concise, professional, executive tone (2-5 short paragraphs, use markdown headers/bullets). Ground every claim in the provided data. Do not invent numbers. Keep the structured data unchanged and echo it back verbatim. Use the conversation history for context when the question references previous topics.',
      ),
      ...history.slice(-10).map((m) => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content }) as ChatMessage),
      {
        role: 'user',
        content: JSON.stringify({ question: message, factualAnswer: ruleAnswer.answer, data: ruleAnswer.data ?? null }),
      },
    ];
    const res = await complete({ provider, model: 'auto', messages, temperature: 0.4, maxTokens: 700 });
    const text = res.text.trim();
    if (!text) return ruleAnswer;
    return {
      answer: text,
      data: ruleAnswer.data,
      model: res.model,
      tokensUsed: res.totalTokens,
      simulated: res.simulated,
    };
  } catch {
    return ruleAnswer;
  }
}
async function answerCopilot(message: string, history: string[] = []): Promise<{ answer: string; data?: unknown }> {
  const lower = message.toLowerCase();
  const recent = (await store.auditLog.findMany({ orderBy: { timestamp: 'desc' }, take: 100 })) as Array<{
    id: string;
    prompt: string;
    promptHash: string;
    rewrittenPrompt: string | null;
    violations: unknown;
    secrets: unknown;
    policiesTriggered: unknown;
    riskScore: number;
    threatLevel: string;
    decision: string;
    timestamp: Date | string;
    llmProvider: string | null;
    user: { id: string; name: string; email: string; department: string } | null;
  }>;
  const weekAgo = Date.now() - 7 * 24 * 3600 * 1000;

  const memoryDept = (() => {
    for (let i = history.length - 1; i >= 0; i--) {
      const h = history[i].toLowerCase();
      const hit = DEPARTMENT_NAMES.find((d) => h.includes(d));
      if (hit) return hit === 'hr' ? 'Human Resources' : hit.charAt(0).toUpperCase() + hit.slice(1);
    }
    return null;
  })();

  const scoped = memoryDept ? recent.filter((r) => r.user?.department?.toLowerCase() === memoryDept.toLowerCase()) : recent;

  if (/(why|blocked)/.test(lower) && /(last|latest|prompt)/.test(lower)) {
    const last = recent[0];
    if (!last) return { answer: 'No audit records yet. Submit a prompt through the scanner to get started.' };
    const violations = (last.violations ?? []) as Array<{ policyName: string; severity: string; reason: string; recommendation: string }>;
    return {
      answer: `The most recent prompt (${last.prompt.slice(0, 80)}…) was **${last.decision}** with a risk score of **${last.riskScore}/100** (${last.threatLevel}).\n\n${violations.length === 0 ? 'No policy violations were recorded.' : `Policy violations:\n${violations.map((v) => `- **${v.policyName}** (${v.severity}): ${v.reason.slice(0, 140)}`).join('\n')}\n\nRecommended action: ${violations[0]?.recommendation ?? 'None'}`}`,
      data: last,
    };
  }

  if (/(highest|riskiest|risk).*(prompt|prompts)|(prompt|prompts).*(risk|highest)/.test(lower)) {
    const sorted = [...recent].sort((a, b) => b.riskScore - a.riskScore).slice(0, 5);
    return {
      answer: `Here are the 5 highest-risk prompts today:\n${sorted.map((r, i) => `${i + 1}. **${r.riskScore}/100** (${r.threatLevel}) — ${r.prompt.slice(0, 90)}… — ${r.user?.name ?? 'Anonymous'} — ${r.decision}`).join('\n')}`,
      data: sorted.map((r) => ({ id: r.id, riskScore: r.riskScore, prompt: r.prompt, decision: r.decision })),
    };
  }

  if (/(which|what) polic|polic.*(trigger|violat)/.test(lower)) {
    const counts = new Map<string, { count: number; regulation: string }>();
    for (const r of recent.filter((x) => new Date(String(x.timestamp)).getTime() > weekAgo)) {
      for (const reg of (r.policiesTriggered ?? []) as string[]) {
        const entry = counts.get(reg) ?? { count: 0, regulation: reg };
        entry.count++;
        counts.set(reg, entry);
      }
    }
    const top = [...counts.entries()].sort((a, b) => b[1].count - a[1].count).slice(0, 5);
    return {
      answer: top.length === 0
        ? 'No policy violations were recorded in the last 7 days. Your policy posture is clean.'
        : `Policy triggers in the last 7 days:\n${top.map(([reg, v]) => `- **${reg}**: ${v.count} time${v.count === 1 ? '' : 's'}`).join('\n')}`,
      data: top.map(([regulation, v]) => ({ regulation, count: v.count })),
    };
  }

  if (/(rewrit)/.test(lower)) {
    const rewritten = recent.filter((r) => r.rewrittenPrompt && r.rewrittenPrompt !== r.prompt).slice(0, 3);
    if (rewritten.length === 0) return { answer: 'No rewritten prompts found in recent history.' };
    return {
      answer: `The last ${rewritten.length} prompts were rewritten before transmission:\n${rewritten.map((r) => `- **Before:** ${r.prompt.slice(0, 90)}…\n  **After:** ${r.rewrittenPrompt?.slice(0, 90)}…`).join('\n')}\n\nRewriting preserves the user's intent while removing sensitive entities.`,
      data: rewritten.map((r) => ({ before: r.prompt, after: r.rewrittenPrompt })),
    };
  }

  if (/(violations|violation).*(week|this week)/.test(lower)) {
    const weekViolations = recent.filter((r) => new Date(String(r.timestamp)).getTime() > weekAgo);
    const risky = weekViolations.filter((r) => r.riskScore >= 35).length;
    return {
      answer: `In the last 7 days: **${weekViolations.length} prompts** were processed, **${risky}** were flagged as risky (score ≥ 35).\n\nRisk breakdown: ${recent.filter((r) => r.riskScore >= 80).length} critical, ${recent.filter((r) => r.riskScore >= 60 && r.riskScore < 80).length} high, ${recent.filter((r) => r.riskScore >= 35 && r.riskScore < 60).length} medium, ${recent.filter((r) => r.riskScore < 35).length} low.`,
      data: { total: weekViolations.length, risky, window: '7d' },
    };
  }

  if (/(category|common|detection)/.test(lower)) {
    const counts = new Map<string, number>();
    for (const r of recent) {
      for (const s of (r.secrets ?? []) as Array<{ label: string }>) {
        counts.set(s.label, (counts.get(s.label) ?? 0) + 1);
      }
    }
    const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8);
    return {
      answer: `Most frequent detection categories:\n${top.map(([label, n], i) => `${i + 1}. **${label}** — ${n} occurrence${n === 1 ? '' : 's'}`).join('\n')}`,
      data: top.map(([category, count]) => ({ category, count })),
    };
  }

  if (/(recommend|improve|suggest)/.test(lower)) {
    const risky = recent.filter((r) => r.riskScore >= 35);
    const violations = recent.flatMap((r) => (r.violations ?? []) as Array<{ policyName: string; regulation: string; recommendation: string }>);
    const policyCounts = new Map<string, { count: number; regulation: string; recommendation: string }>();
    for (const v of violations) {
      const entry = policyCounts.get(v.policyName) ?? { count: 0, regulation: v.regulation, recommendation: v.recommendation };
      entry.count++;
      policyCounts.set(v.policyName, entry);
    }
    const topPolicy = [...policyCounts.entries()].sort((a, b) => b[1].count - a[1].count)[0];
    const secretCounts = new Map<string, number>();
    for (const r of recent) {
      for (const s of (r.secrets ?? []) as Array<{ label: string }>) secretCounts.set(s.label, (secretCounts.get(s.label) ?? 0) + 1);
    }
    const topSecret = [...secretCounts.entries()].sort((a, b) => b[1] - a[1])[0];

    const recs = [
      topPolicy
        ? `**Policy exposure** — "${topPolicy[0]}" triggered ${topPolicy[1].count} times (${topPolicy[1].regulation}). ${topPolicy[1].recommendation ?? 'Review and tighten the detection rules.'}`
        : '**Policy exposure** — no violations in recent history. Keep current policy packs active.',
      topSecret
        ? `**Data leakage** — "${topSecret[0]}" is your most leaked secret type (${topSecret[1]} occurrences). Consider blocking it at the gateway or training the affected team.`
        : '**Data leakage** — no secret types detected recently. Good hygiene.',
      risky.length > 0
        ? `**High-risk prompts** — ${risky.length} of the last ${recent.length} prompts exceeded the risk threshold. Enforce the 35-point floor and route risky prompts to review.`
        : '**High-risk prompts** — no prompts exceeded the risk threshold recently.',
      `**Compliance** — keep GDPR, HIPAA, PCI DSS, SOC 2 and ISO 27001 packs enabled and enable auto-rewrite for medium-risk requests.`,
    ];
    return {
      answer: `Based on the last ${recent.length} audit records, here are my recommendations:\n\n${recs.map((r, i) => `${i + 1}. ${r}`).join('\n\n')}`,
      data: { risky: risky.length, topPolicy: topPolicy?.[0], topSecret: topSecret?.[0] },
    };
  }

  if (/(department|team|org)/.test(lower)) {
    const deptMap = new Map<string, { total: number; risky: number; scoreSum: number }>();
    for (const r of recent) {
      const dept = r.user?.department;
      if (!dept) continue;
      const entry = deptMap.get(dept) ?? { total: 0, risky: 0, scoreSum: 0 };
      entry.total++;
      entry.scoreSum += r.riskScore;
      if (r.riskScore >= 35) entry.risky++;
      deptMap.set(dept, entry);
    }
    const rows = [...deptMap.entries()]
      .map(([dept, v]) => ({ dept, risk: v.total ? Math.round((v.risky / v.total) * 100) : 0, avg: v.total ? Math.round(v.scoreSum / v.total) : 0 }))
      .sort((a, b) => b.risk - a.risk);
    return {
      answer: rows.length === 0
        ? 'No department metadata is attached to recent records yet.'
        : `Department risk exposure (risk index = % of prompts above threshold):\n${rows.map((r, i) => `${i + 1}. **${r.dept}** — index ${r.risk}%, avg score ${r.avg}`).join('\n')}`,
      data: rows,
    };
  }

  // ---------- EXECUTIVE COPILOT (telemetry-grounded) ----------

  if (/(why|reason).*(threat|risk|incident|increase|spike|grew|rise)/.test(lower) || /threat.*(increas|rise|spike|grow)/.test(lower)) {
    const dayAgo = Date.now() - 24 * 3600 * 1000;
    const weekAgo = Date.now() - 7 * 24 * 3600 * 1000;
    const today = scoped.filter((r) => new Date(String(r.timestamp)).getTime() > dayAgo);
    const thisWeek = scoped.filter((r) => new Date(String(r.timestamp)).getTime() > weekAgo);
    const secretCounts = new Map<string, number>();
    for (const r of thisWeek) for (const s of (r.secrets ?? []) as Array<{ label: string }>) secretCounts.set(s.label, (secretCounts.get(s.label) ?? 0) + 1);
    const topSecret = [...secretCounts.entries()].sort((a, b) => b[1] - a[1])[0];
    const deptMap = new Map<string, number>();
    for (const r of thisWeek) {
      const dept = r.user?.department;
      if (dept) deptMap.set(dept, (deptMap.get(dept) ?? 0) + 1);
    }
    const topDept = [...deptMap.entries()].sort((a, b) => b[1] - a[1])[0];
    return {
      answer: `${memoryDept ? `Analysing **${memoryDept}** (recalled from our earlier conversation).\n\n` : ''}Threat volume this week: **${thisWeek.filter((r) => r.riskScore >= 35).length}** risky prompts (of ${thisWeek.length} total), with **${today.filter((r) => r.riskScore >= 60).length}** high/critical events in the last 24h.\n\nThe primary drivers:\n- **Secret type:** ${topSecret?.[0] ?? 'n/a'} (${topSecret?.[1] ?? 0} occurrences)\n- **Hotspot department:** ${topDept?.[0] ?? 'n/a'}\n\nRecommended: enforce auto-rewrite for ${topSecret?.[0] ?? 'that'} and re-run the affected team's training.`,
      data: { riskyWeek: thisWeek.filter((r) => r.riskScore >= 35).length, topSecret: topSecret?.[0], topDept: topDept?.[0], scopedTo: memoryDept },
    };
  }

  if (/(compare|vs|versus|yesterday|today).*(yesterday|today|last|previous)/.test(lower)) {
    const now = Date.now();
    const todayStart = new Date(now).setHours(0, 0, 0, 0);
    const yesterdayStart = todayStart - 24 * 3600 * 1000;
    const today = scoped.filter((r) => new Date(String(r.timestamp)).getTime() >= todayStart);
    const yesterday = scoped.filter((r) => {
      const t = new Date(String(r.timestamp)).getTime();
      return t >= yesterdayStart && t < todayStart;
    });
    const summarize = (arr: any[]) => ({
      total: arr.length,
      blocked: arr.filter((r) => r.decision === 'BLOCK').length,
      risky: arr.filter((r) => r.riskScore >= 35).length,
      avg: arr.length ? Math.round(arr.reduce((a, r) => a + r.riskScore, 0) / arr.length) : 0,
    });
    const sToday = summarize(today);
    const sYesterday = summarize(yesterday);
    const delta = sToday.risky - sYesterday.risky;
    return {
      answer: `${memoryDept ? `Comparing **${memoryDept}** traffic (recalled from our earlier conversation):\n\n` : ''}**Today vs yesterday:**\n\n| Metric | Today | Yesterday | Δ |\n|---|---|---|---|\n| Prompts | ${sToday.total} | ${sYesterday.total} | ${sToday.total - sYesterday.total} |\n| Blocked | ${sToday.blocked} | ${sYesterday.blocked} | ${sToday.blocked - sYesterday.blocked} |\n| Risky (≥35) | ${sToday.risky} | ${sYesterday.risky} | ${delta >= 0 ? '+' : ''}${delta} |\n| Avg risk | ${sToday.avg} | ${sYesterday.avg} | ${sToday.avg - sYesterday.avg} |\n\n${delta > 0 ? 'Risky traffic is **up** — investigate the drivers above.' : delta < 0 ? 'Risky traffic is **down** — posture improving.' : 'Risky traffic is **flat** — posture stable.'}`,
      data: { today: sToday, yesterday: sYesterday, scopedTo: memoryDept },
    };
  }

  if (/(trend|today|this week|weekly)/.test(lower)) {
    const dayAgo = Date.now() - 24 * 3600 * 1000;
    const today = recent.filter((r) => new Date(String(r.timestamp)).getTime() > dayAgo);
    const blocked = today.filter((r) => r.decision === 'BLOCK').length;
    const rewritten = today.filter((r) => r.decision === 'REWRITE').length;
    const flagged = today.filter((r) => r.decision === 'FLAG').length;
    const avg = today.length ? Math.round(today.reduce((a, r) => a + r.riskScore, 0) / today.length) : 0;
    return {
      answer: `Today's activity (last 24h): **${today.length} prompts** processed, **${blocked} blocked**, **${rewritten} rewritten**, **${flagged} flagged**. Average risk score **${avg}/100**.\n\n${today.length === 0 ? 'No events in the window yet.' : 'The security posture is ' + (avg >= 60 ? 'elevated — consider investigating recent spikes.' : avg >= 35 ? 'moderate — monitor closely.' : 'stable.')}`,
      data: { total: today.length, blocked, rewritten, flagged, avg },
    };
  }

  if (/(gdpr|hipaa|pci|soc 2|iso|compliance|regulation|regulations)/.test(lower) && /(show|list|violation|which|status)/.test(lower)) {
    const weekAgo = Date.now() - 7 * 24 * 3600 * 1000;
    const byReg = new Map<string, { count: number; policies: Set<string>; depts: Set<string> }>();
    for (const r of recent.filter((x) => new Date(String(x.timestamp)).getTime() > weekAgo)) {
      const violations = (r.violations ?? []) as Array<{ regulation: string; policyName: string }>;
      for (const v of violations) {
        const reg = v.regulation;
        const entry = byReg.get(reg) ?? { count: 0, policies: new Set(), depts: new Set() };
        entry.count++;
        if (v.policyName) entry.policies.add(v.policyName);
        if (r.user?.department) entry.depts.add(r.user.department);
        byReg.set(reg, entry);
      }
    }
    const rows = [...byReg.entries()].sort((a, b) => b[1].count - a[1].count).slice(0, 6);
    if (rows.length === 0) {
      return { answer: '**No violations recorded** in the last 7 days. Your compliance posture is clean across GDPR, HIPAA, PCI DSS, SOC 2 and ISO 27001.', data: [] };
    }
    return {
      answer: `Compliance violations in the last 7 days:\n${rows.map(([reg, v]) => `- **${reg}**: ${v.count} violation${v.count === 1 ? '' : 's'} · ${[...v.policies].join(', ')} · ${[...v.depts].join(', ')}`).join('\n')}\n\nFocus areas: ${rows[0][0]} (${rows[0][1].count}). See the Compliance page for enforcement details.`,
      data: rows.map(([regulation, v]) => ({ regulation, count: v.count, policies: [...v.policies], departments: [...v.depts] })),
    };
  }

  if (/(posture|status|health|summary|executive|overview|situation)/.test(lower)) {
    const risky = recent.filter((r) => r.riskScore >= 35).length;
    const blocked = recent.filter((r) => r.decision === 'BLOCK').length;
    const rewritten = recent.filter((r) => r.decision === 'REWRITE').length;
    const critical = recent.filter((r) => r.riskScore >= 80).length;
    const companyScore = recent.length ? Math.max(0, Math.min(100, Math.round(100 - (risky / recent.length) * 100 * 0.7))) : 96;
    const deptMap = new Map<string, { risky: number; total: number }>();
    for (const r of recent) {
      const dept = r.user?.department;
      if (!dept) continue;
      const e = deptMap.get(dept) ?? { risky: 0, total: 0 };
      e.total++;
      if (r.riskScore >= 35) e.risky++;
      deptMap.set(dept, e);
    }
    const topDept = [...deptMap.entries()].map(([name, v]) => ({ name, idx: v.total ? Math.round((v.risky / v.total) * 100) : 0 })).sort((a, b) => b.idx - a.idx)[0];
    return {
      answer: `**Executive Security Summary**\n\n- **Company security score:** ${companyScore}/100\n- **Prompts audited:** ${recent.length}\n- **Threats intercepted:** ${blocked} blocked · ${rewritten} rewritten\n- **Critical events:** ${critical}\n- **Highest-risk department:** ${topDept?.name ?? 'n/a'} (index ${topDept?.idx ?? 0}%)\n\nPosture: ${companyScore >= 85 ? '**Strong** — defenses are holding and the organization is operating at ADVANCED maturity.' : companyScore >= 65 ? '**Stable** — moderate risk exposure; continue monitoring hotspot teams.' : '**At risk** — prioritize the highest-risk departments and enforce auto-rewrite.'}\n\nRecommendation: ${topDept && topDept.idx >= 50 ? `Schedule training for ${topDept.name} and enable auto-rewrite for their traffic.` : 'Maintain current policy packs and review the monthly compliance report.'}`,
      data: { companyScore, blocked, rewritten, critical, topDept },
    };
  }

  return {
    answer:
      'I can analyse SentinelX audit data to answer questions like: why a prompt was blocked, today\'s highest-risk prompts, policy triggers, rewriting outcomes, weekly violation counts, department risk, and security recommendations. Try one of the suggested questions.',
  };
}

const start = async () => {
  for (const warning of envReport.warnings) {
    fastify.log.warn(`[env] ${warning}`);
  }
  if (envReport.simulatedMode) {
    fastify.log.warn(
      `[env] Starting in SIMULATED mode — ${envReport.providers.length} providers available (none configured).`
    );
  } else {
    const configured = envReport.providers.filter((p) => p.configured).map((p) => p.id);
    fastify.log.info(`[env] LLM providers configured: ${configured.join(', ')}`);
  }

  // Prevent process exit on unhandled errors
  process.on('unhandledRejection', (reason, promise) => {
    fastify.log.error({ err: reason, promise }, 'Unhandled Rejection');
  });
  process.on('uncaughtException', (err) => {
    fastify.log.error({ err }, 'Uncaught Exception');
  });
  process.on('SIGTERM', async () => {
    fastify.log.info('SIGTERM received, closing gracefully');
    await fastify.close();
    process.exit(0);
  });
  process.on('SIGINT', async () => {
    fastify.log.info('SIGINT received, closing gracefully');
    await fastify.close();
    process.exit(0);
  });

  try {
    await fastify.listen({ port: PORT, host: '0.0.0.0' });
    fastify.log.info(`🚀 SentinelX API listening on http://0.0.0.0:${PORT}`);
    
    // Keep process alive and handle background tasks safely
    const keepAlive = setInterval(() => {
      // Keep process alive for Railway health checks
    }, 30000);
    
    // Ensure keepAlive doesn't prevent graceful shutdown
    process.on('SIGTERM', async () => {
      clearInterval(keepAlive);
      fastify.log.info('SIGTERM received, closing gracefully');
      await fastify.close();
      process.exit(0);
    });
    process.on('SIGINT', async () => {
      clearInterval(keepAlive);
      fastify.log.info('SIGINT received, closing gracefully');
      await fastify.close();
      process.exit(0);
    });
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
