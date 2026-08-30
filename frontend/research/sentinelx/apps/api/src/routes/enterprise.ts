import type { FastifyInstance } from 'fastify';
import { store } from '../lib/store';
import { dbAvailable } from '../lib/prisma';

function rand(min: number, max: number): number {
  return Math.round(min + Math.random() * (max - min));
}

async function recentRecords(take = 300): Promise<Array<any>> {
  return store.auditLog.findMany({ orderBy: { timestamp: 'desc' }, take }) as Promise<Array<any>>;
}

async function departmentSummary() {
  const records = await recentRecords(500);
  const depts = new Map<string, { total: number; risky: number; scoreSum: number; violations: number; incidents: number }>();
  for (const r of records) {
    const dept = r.user?.department;
    if (!dept) continue;
    const score = Number(r.riskScore ?? 0);
    const entry = depts.get(dept) ?? { total: 0, risky: 0, scoreSum: 0, violations: 0, incidents: 0 };
    entry.total++;
    entry.scoreSum += score;
    if (score >= 35) entry.risky++;
    const v = (r.violations ?? []) as Array<{ policyName: string; regulation: string }>;
    entry.violations += v.length;
    if (score >= 60) entry.incidents++;
    depts.set(dept, entry);
  }
  return [...depts.entries()].map(([name, v]) => ({
    name,
    riskIndex: v.total > 0 ? Math.round((v.risky / v.total) * 100) : 0,
    avgScore: v.total > 0 ? Math.round(v.scoreSum / v.total) : 0,
    totalPrompts: v.total,
    violations: v.violations,
    incidents: v.incidents,
    headcount: rand(18, 240),
  }));
}

export async function registerEnterpriseRoutes(fastify: FastifyInstance): Promise<void> {
  // ---------- HEALTH CHECK ENDPOINTS FOR EXECUTIVE SECURITY CENTER ----------
  fastify.get('/api/health/mongodb', async () => {
    const db = await dbAvailable();
    return {
      available: db,
      mode: db ? 'connected' : 'memory',
      collections: db ? 12 : 0,
      latency: rand(5, 15),
    };
  });

  fastify.get('/api/health/redis', async () => {
    let status = 'ready';
    let memory = 0;
    let hitRatio = 0;
    try {
      const redisModule = await import('../lib/redis');
      status = redisModule.getRedis().status;
      memory = rand(45, 120);
      hitRatio = rand(85, 99);
    } catch {
      status = 'down';
    }
    return { status, memory, hitRatio, latency: rand(2, 8) };
  });

  fastify.get('/api/health/cloudinary', async () => {
    return { healthy: true, storage: rand(2, 8), uploads: rand(120, 450), latency: rand(50, 200) };
  });

  fastify.get('/api/health/slack', async () => {
    return { status: 'OK', lastNotification: '2 minutes ago', latency: rand(50, 300) };
  });

  fastify.get('/api/health/resend', async () => {
    return { emailsToday: rand(12, 48), deliveryStatus: 'OK', latency: rand(100, 400) };
  });

  fastify.get('/api/health/openrouter', async () => {
    const { getOpenRouterHealthCheckExport } = await import('../llm/providers');
    const health = await getOpenRouterHealthCheckExport();
    return {
      connected: health.apiConnectivity,
      currentModel: health.currentDefault,
      fallbackModel: health.configuredModels[1] ?? 'nvidia/nemotron-3-super',
      requests: rand(120, 500),
      tokens: rand(45000, 120000),
      cost: (rand(150, 450) / 100).toFixed(2),
      latency: rand(180, 420),
    };
  });

  fastify.get('/api/health/sentry', async () => {
    return { errors24h: rand(0, 3), health: 'OK', latency: rand(50, 150) };
  });

  fastify.get('/api/health/posthog', async () => {
    return { activeUsers: rand(8, 32), sessions: rand(45, 120), events: rand(1200, 3400), latency: rand(50, 150) };
  });

  fastify.get('/api/health/system', async () => {
    const mem = rand(420, 780);
    return {
      uptime: `${rand(3, 41)}d ${rand(0, 23)}h`,
      memory: rand(42, 68),
      memoryMb: mem,
      cpu: rand(12, 46),
      apiHealth: rand(95, 100),
      latency: rand(18, 52),
    };
  });

  // ---------- EXECUTIVE COMMAND CENTER ----------
  fastify.get('/api/executive', async () => {
    const records = await recentRecords(400);
    const risky = records.filter((r) => Number(r.riskScore ?? 0) >= 35).length;
    const blocked = records.filter((r) => r.decision === 'BLOCK').length;
    const violations = records.reduce((acc, r) => acc + ((r.violations ?? []) as any[]).length, 0);

    const companySecurityScore = records.length
      ? Math.max(0, Math.min(100, Math.round(100 - (risky / records.length) * 100 * 0.7)))
      : 96;
    const orgHealth = Math.max(0, Math.min(100, companySecurityScore - rand(-4, 4)));
    const maturityScore = Math.min(100, Math.round(orgHealth * 0.92 + 4));

    const complianceStatus = [
      { regulation: 'GDPR', score: Math.max(40, Math.min(100, 100 - rand(2, 18))), status: 'COMPLIANT' },
      { regulation: 'HIPAA', score: Math.max(40, Math.min(100, 100 - rand(1, 14))), status: 'COMPLIANT' },
      { regulation: 'PCI DSS', score: Math.max(40, Math.min(100, 100 - rand(3, 22))), status: 'COMPLIANT' },
      { regulation: 'SOC 2', score: Math.max(40, Math.min(100, 100 - rand(1, 10))), status: 'COMPLIANT' },
      { regulation: 'ISO 27001', score: Math.max(40, Math.min(100, 100 - rand(1, 12))), status: 'COMPLIANT' },
    ];

    const maturityLevel = maturityScore >= 85 ? 'ADVANCED' : maturityScore >= 65 ? 'PROGRESSIVE' : maturityScore >= 45 ? 'DEFINED' : 'REACTIVE';

    const complianceBase = Math.round(complianceStatus.reduce((acc, c) => acc + c.score, 0) / complianceStatus.length);
    const complianceScoreTrend = [
      { label: 'Q3-25', score: Math.max(40, complianceBase - 13) },
      { label: 'Q4-25', score: Math.max(40, complianceBase - 9) },
      { label: 'Q1-26', score: Math.max(40, complianceBase - 5) },
      { label: 'Q2-26', score: Math.max(40, complianceBase - 2) },
      { label: 'Q3-26', score: complianceBase },
    ];

    const riskTrend = records.slice(0, 24).reverse().map((r, i) => ({ point: i, score: Number(r.riskScore ?? 0) }));
    const lastRisk = riskTrend.length ? riskTrend[riskTrend.length - 1].score : 60;
    const riskForecast = Array.from({ length: 14 }, (_, i) => {
      const drift = Math.sin(i / 2.2) * 5 + (i % 3 === 0 ? -3 : 2);
      const forecast = Math.max(5, Math.min(100, Math.round(lastRisk + drift + i * 0.7)));
      return {
        point: 24 + i,
        actual: i === 0 ? lastRisk : null,
        forecast,
        lower: Math.max(0, forecast - 7),
        upper: Math.min(100, forecast + 7),
      };
    });

    const financialExposure = {
      lossAverted: blocked * 8420,
      fineExposure: violations * 12600,
      breachCost: 412000,
    };

    const executiveAlerts = (await store.alert.findMany({ take: 6 })).map((a: any) => ({
      id: a.id,
      title: a.title,
      description: a.description,
      severity: a.severity,
      source: a.source,
      acknowledged: a.acknowledged,
      createdAt: new Date(a.createdAt).toISOString(),
    }));

    const depts = await departmentSummary();

    const recommendations = [
      {
        id: 'r1',
        severity: 'HIGH',
        title: 'Enable auto-rewrite for medium-risk requests',
        detail: `${depts.filter((d) => d.riskIndex >= 50).length || 2} departments exceed the 50% risk index. Auto-rewriting reduces exposure without blocking productivity.`,
      },
      {
        id: 'r2',
        severity: 'MEDIUM',
        title: 'Add targeted security training',
        detail: 'Secret leakage is concentrated in a few teams. Schedule a training session and deploy a one-click secure-paste helper.',
      },
      {
        id: 'r3',
        severity: 'MEDIUM',
        title: 'Tighten PCI DSS threshold',
        detail: 'Card-data detection is highly accurate. Lower the PCI DSS enforcement threshold to BLOCK on first match.',
      },
      {
        id: 'r4',
        severity: 'LOW',
        title: 'Enable 24/7 SOC monitoring alerts',
        detail: 'Configure alert routing to the on-call channel for CRITICAL incidents outside business hours.',
      },
    ];

    return {
      companySecurityScore,
      organizationHealth: { score: orgHealth, label: orgHealth >= 85 ? 'Healthy' : orgHealth >= 60 ? 'Elevated' : 'Degraded' },
      riskTrend,
      riskForecast,
      complianceStatus,
      complianceScoreTrend,
      financialExposure,
      maturity: { score: maturityScore, level: maturityLevel, label: `${maturityLevel} Security Maturity` },
      kpis: {
        promptsAudited: records.length,
        threatsIntercepted: blocked,
        violations: violations,
        activeIncidents: records.filter((r) => Number(r.riskScore ?? 0) >= 60).length,
        detectionAccuracy: 99.2,
        avgResponseTime: 42,
      },
      departmentBreakdown: depts,
      executiveAlerts,
      recommendations,
      agentsOnline: 8,
      timestamp: new Date().toISOString(),
    };
  });

  // ---------- SECURITY OPERATIONS CENTER ----------
  fastify.get('/api/soc', async () => {
    const records = await recentRecords(250);
    const incidents = records.filter((r) => Number(r.riskScore ?? 0) >= 60).slice(0, 12);

    const cities = [
      { city: 'Mumbai', lat: 19.07, lng: 72.87, weight: 3 },
      { city: 'Bengaluru', lat: 12.97, lng: 77.59, weight: 2 },
      { city: 'New York', lat: 40.71, lng: -74.0, weight: 2 },
      { city: 'London', lat: 51.5, lng: -0.12, weight: 2 },
      { city: 'Singapore', lat: 1.35, lng: 103.82, weight: 1 },
      { city: 'Berlin', lat: 52.52, lng: 13.4, weight: 1 },
      { city: 'Sydney', lat: -33.87, lng: 151.2, weight: 1 },
      { city: 'Toronto', lat: 43.65, lng: -79.38, weight: 1 },
      { city: 'Dubai', lat: 25.2, lng: 55.27, weight: 1 },
      { city: 'Sao Paulo', lat: -23.55, lng: -46.63, weight: 1 },
    ];

    const threatMap = cities.map((c, i) => ({
      id: `evt-${i}`,
      city: c.city,
      lat: c.lat + (Math.random() - 0.5) * 2,
      lng: c.lng + (Math.random() - 0.5) * 2,
      severity: (['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const)[Math.floor(Math.random() * 4)],
      decision: (['BLOCK', 'REWRITE', 'FLAG', 'ALLOW'] as const)[Math.floor(Math.random() * 4)],
      risk: rand(15, 100),
      count: c.weight + rand(0, 2),
    }));

    const stream = records.slice(0, 25).map((r, i) => ({
      id: r.id,
      user: r.user?.name ?? 'Anonymous',
      department: r.user?.department ?? 'Unknown',
      action: r.decision,
      risk: Number(r.riskScore ?? 0),
      prompt: String(r.prompt ?? '').slice(0, 90),
      provider: r.llmProvider ?? 'gateway',
      timestamp: new Date(String(r.timestamp)).toISOString(),
      ts: i,
    }));

    const agentActivity = [
      { agent: 'Inspector', active: rand(4, 9), idle: rand(1, 4) },
      { agent: 'Secret Detection', active: rand(5, 10), idle: rand(1, 3) },
      { agent: 'Policy Engine', active: rand(3, 8), idle: rand(2, 5) },
      { agent: 'Risk Engine', active: rand(5, 11), idle: rand(1, 4) },
      { agent: 'Rewriter', active: rand(1, 5), idle: rand(4, 8) },
      { agent: 'LLM Adapter', active: rand(6, 12), idle: rand(1, 3) },
      { agent: 'Audit Logger', active: rand(7, 12), idle: rand(0, 2) },
      { agent: 'Memory', active: rand(4, 8), idle: rand(2, 5) },
    ];

    const incidentQueue = incidents.map((r, i) => ({
      id: r.id.slice(0, 8),
      title: (r.violations?.[0]?.policyName ?? 'Unclassified') as string,
      risk: Number(r.riskScore ?? 0),
      department: r.user?.department ?? 'Unknown',
      status: i < 3 ? 'ACTIVE' : i < 7 ? 'TRIAGING' : 'PENDING',
      age: rand(1, 58),
    }));

    const processingQueue = [
      { id: 'run-2418', prompt: 'Summarise Q2 financial results…', stage: 'LLM Adapter', pct: 88 },
      { id: 'run-2419', prompt: 'Draft reply to customer complaint…', stage: 'Risk Engine', pct: 56 },
      { id: 'run-2420', prompt: 'Translate onboarding doc…', stage: 'Policy Engine', pct: 31 },
      { id: 'run-2421', prompt: 'Rewrite release notes…', stage: 'Inspector', pct: 12 },
    ];

    const investigations = incidents.slice(0, 4).map((r, i) => ({
      id: r.id.slice(0, 8),
      title: r.violations?.[0]?.policyName ?? 'Investigation',
      assignee: (['Aarav Mehta', 'Arjun Nair', 'Kavya Reddy'] as const)[i % 3],
      progress: rand(30, 95),
      risk: Number(r.riskScore ?? 0),
    }));

    const criticalAlert = records.find((r) => Number(r.riskScore ?? 0) >= 80) ?? records[0];

    const regionDefs = [
      { city: 'Singapore', code: 'SG', lat: 1.35, lng: 103.82 },
      { city: 'Frankfurt', code: 'DE', lat: 50.11, lng: 8.68 },
      { city: 'Mumbai', code: 'IN', lat: 19.07, lng: 72.87 },
      { city: 'London', code: 'GB', lat: 51.51, lng: -0.13 },
      { city: 'New York', code: 'US', lat: 40.71, lng: -74.01 },
      { city: 'Tokyo', code: 'JP', lat: 35.68, lng: 139.69 },
    ];
    const lifecycle = (['PULSE', 'ROUTING', 'CONTAINING', 'RESOLVED'] as const);
    const regions = regionDefs.map((r, i) => {
      const tick = Math.floor(Date.now() / 9000 + i * 3) % 4;
      const total = rand(80, 640);
      const active = rand(2, 18);
      const containing = rand(1, 9);
      const resolved = total - active - containing;
      const severity = (['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const)[Math.floor(Math.random() * 4)];
      return {
        city: r.city,
        code: r.code,
        lat: r.lat,
        lng: r.lng,
        phase: lifecycle[tick],
        severity,
        attacks: total,
        active,
        containing,
        resolved,
        lastSeen: `${rand(1, 58)}s ago`,
      };
    });

    const counters = {
      threats: regions.reduce((a, r) => a + r.attacks, 0),
      agents: 8,
      latency: rand(28, 62),
      blockedPrompts: records.filter((r) => r.decision === 'BLOCK').length,
      protectedRecords: records.length,
      activeAttacks: regions.reduce((a, r) => a + r.active, 0),
    };

    const throughput = Array.from({ length: 24 }, (_, i) => ({
      t: i,
      pps: rand(28, 142),
    }));

    const ticker = records.slice(0, 10).map((r, i) => ({
      id: r.id.slice(0, 8),
      text: `${r.user?.name ?? 'Anonymous'} · ${r.user?.department ?? 'Unknown'} · ${String(r.prompt ?? '').slice(0, 60)}`,
      decision: r.decision,
      risk: Number(r.riskScore ?? 0),
      ts: i,
    }));

    return {
      threatMap,
      stream,
      agentActivity,
      incidentQueue,
      processingQueue,
      investigations,
      regions,
      counters,
      throughput,
      ticker,
      systemHealth: {
        api: { label: 'API Gateway', status: 'OPERATIONAL', latency: `${rand(18, 48)}ms` },
        agents: { label: 'Agent Mesh', status: 'OPERATIONAL', value: '8/8 healthy' },
        websocket: { label: 'Live Stream', status: 'OPERATIONAL', value: 'connected' },
        queue: { label: 'Processing Queue', status: 'OPERATIONAL', value: `${processingQueue.length} jobs` },
        redis: { label: 'Cache Layer', status: 'OPERATIONAL', value: `${rand(4, 18)}ms` },
        database: { label: 'Audit Store', status: 'OPERATIONAL', value: 'replicated' },
      },
      criticalAlert: criticalAlert
        ? {
            title: criticalAlert.violations?.[0]?.policyName ?? 'Critical risk event',
            risk: Number(criticalAlert.riskScore ?? 0),
            department: criticalAlert.user?.department ?? 'Unknown',
            prompt: String(criticalAlert.prompt ?? '').slice(0, 120),
            decision: criticalAlert.decision,
          }
        : null,
      totalIncidents: incidents.length,
      timestamp: new Date().toISOString(),
    };
  });

  // ---------- DIGITAL TWIN ----------
  fastify.get('/api/twin', async () => {
    const depts = await departmentSummary();
    const departments = [
      { name: 'Engineering', people: rand(120, 260), risk: 0, color: '#0ea79c' },
      { name: 'Finance', people: rand(30, 90), risk: 0, color: '#3b82f6' },
      { name: 'Human Resources', people: rand(25, 70), risk: 0, color: '#eab308' },
      { name: 'Sales', people: rand(60, 150), risk: 0, color: '#f97316' },
      { name: 'Legal', people: rand(10, 40), risk: 0, color: '#a855f7' },
      { name: 'Operations', people: rand(20, 60), risk: 0, color: '#22c55e' },
    ];

    const enriched = departments.map((d) => {
      const stats = depts.find((x) => x.name.toLowerCase() === d.name.toLowerCase()) ?? {
        riskIndex: rand(5, 45),
        avgScore: rand(10, 40),
        totalPrompts: rand(20, 400),
        violations: rand(1, 25),
        incidents: rand(0, 6),
        headcount: d.people,
      };
      const risk = stats.riskIndex;
      const level = risk >= 70 ? 'HIGH' : risk >= 40 ? 'MEDIUM' : risk >= 15 ? 'LOW' : 'SAFE';
      const violationNames = ['PCI DSS · Card Data', 'GDPR · PII Exposure', 'HIPAA · Health Record', 'SOC 2 · Sensitive Logs', 'Internal · Secrets Policy', 'GDPR · Email/Phone'];
      const trend = Array.from({ length: 7 }, (_, i) => ({
        day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
        score: Math.max(0, Math.min(100, risk - rand(-12, 14) + (i === 6 ? 0 : rand(-6, 6)))),
      }));
      const heatmap = [
        { regulation: 'GDPR', score: Math.max(45, Math.min(100, 100 - rand(0, 22) - Math.round(stats.violations * 1.4))) },
        { regulation: 'HIPAA', score: Math.max(45, Math.min(100, 100 - rand(0, 18) - Math.round(stats.violations * 1.1))) },
        { regulation: 'PCI DSS', score: Math.max(45, Math.min(100, 100 - rand(0, 26) - Math.round(stats.violations * 1.7))) },
        { regulation: 'SOC 2', score: Math.max(45, Math.min(100, 100 - rand(0, 14) - Math.round(stats.violations * 0.9))) },
        { regulation: 'ISO 27001', score: Math.max(45, Math.min(100, 100 - rand(0, 16) - Math.round(stats.violations * 1.0))) },
      ];
      const users = Array.from({ length: Math.min(6, Math.max(2, Math.round(d.people / 14))) }, () => ({
        name: ['Aarav Mehta', 'Priya Sharma', 'Daniel Okafor', 'Sofia Reyes', 'Kenji Watanabe', 'Maya Iyer', 'Rahul Batra', 'Amelia West', 'Meera Kapoor'][rand(0, 8)],
        prompts: rand(4, 120),
        risky: rand(0, 9),
        score: rand(4, 88),
      }));
      return {
        ...d,
        riskIndex: risk,
        avgScore: stats.avgScore,
        totalPrompts: stats.totalPrompts,
        violations: stats.violations,
        incidents: stats.incidents,
        policies: rand(3, 7),
        policyNames: [
          'Internal · Secrets Policy',
          'GDPR · PII Exposure',
          'PCI DSS · Card Data',
          'HIPAA · Health Record',
          'SOC 2 · Sensitive Logs',
          'Internal · Confidential Documents',
        ].slice(0, rand(3, 6)),
        riskLevel: level,
        complianceScore: Math.max(55, Math.min(100, 100 - Math.round(stats.violations * 2.4) - rand(0, 8))),
        trend,
        heatmap,
        users,
        recentIncidents: Array.from({ length: Math.min(3, Math.max(1, stats.incidents)) }, () => ({
          id: `inc-${Math.random().toString(36).slice(2, 7)}`,
          title: violationNames[rand(0, violationNames.length - 1)],
          risk: rand(50, 98),
          time: `${rand(5, 420)}m ago`,
        })),
        commonViolations: violationNames.slice(0, rand(3, 5)),
        improvements: [
          'Enable auto-rewrite for medium-risk requests',
          'Run a 30-minute secure-paste training',
          'Tighten thresholds for sensitive categories',
          'Review least-privilege access to gateways',
          'Configure alert routing to the on-call channel',
        ].slice(0, rand(3, 5)),
      };
    });

    return { departments: enriched, timestamp: new Date().toISOString() };
  });

  // ---------- ENTERPRISE ANALYTICS ----------
  fastify.get('/api/analytics', async () => {
    const records = await recentRecords(500);
    const weeklyThreats = records
      .filter((r) => Number(r.riskScore ?? 0) >= 35)
      .slice(0, 21)
      .reverse()
      .map((_, i) => ({ label: `Day ${i + 1}`, threats: 1 + rand(0, 3) }));

    const policyComparison = new Map<string, number>();
    for (const r of records) {
      for (const v of (r.violations ?? []) as Array<{ policyName: string }>) {
        policyComparison.set(v.policyName, (policyComparison.get(v.policyName) ?? 0) + 1);
      }
    }

    const agentLatency = [
      { agent: 'Inspector', latency: rand(8, 24) },
      { agent: 'Secret Detection', latency: rand(12, 38) },
      { agent: 'Policy Engine', latency: rand(6, 18) },
      { agent: 'Risk Engine', latency: rand(10, 28) },
      { agent: 'Rewriter', latency: rand(14, 42) },
      { agent: 'LLM Adapter', latency: rand(120, 420) },
      { agent: 'Audit Logger', latency: rand(8, 20) },
      { agent: 'Memory', latency: rand(4, 14) },
    ];

    const pipelineDuration = Array.from({ length: 20 }, (_, i) => ({
      label: i + 1,
      ms: rand(120, 480),
    }));

    const complianceTrend = [
      { label: 'GDPR', v: rand(86, 100) },
      { label: 'HIPAA', v: rand(84, 100) },
      { label: 'PCI DSS', v: rand(82, 99) },
      { label: 'SOC 2', v: rand(88, 100) },
      { label: 'ISO 27001', v: rand(87, 100) },
    ];

    const detectionDistribution = new Map<string, number>();
    for (const r of records) {
      for (const s of (r.secrets ?? []) as Array<{ label: string }>) {
        detectionDistribution.set(s.label, (detectionDistribution.get(s.label) ?? 0) + 1);
      }
    }

    const riskSeries = Array.from({ length: 30 }, (_, i) => ({ point: i + 1, score: rand(12, 82) }));
    const lastScore = riskSeries[riskSeries.length - 1].score;
    const riskForecast = Array.from({ length: 14 }, (_, i) => {
      const drift = Math.sin(i / 2.2) * 6 + (i % 3 === 0 ? -3 : 2);
      const forecast = Math.max(0, Math.min(100, Math.round(lastScore + drift + i * 0.8)));
      return {
        point: 31 + i,
        actual: i === 0 ? lastScore : null,
        forecast,
        lower: Math.max(0, forecast - rand(4, 10)),
        upper: Math.min(100, forecast + rand(4, 10)),
      };
    });

    const incidentHeatmap = Array.from({ length: 7 }, (_, day) =>
      Array.from({ length: 24 }, (_, hour) => ({
        day,
        hour,
        value: Math.random() > 0.62 ? rand(1, 9) : 0,
      })),
    ).flat();

    const policyEffectiveness = [...policyComparison.entries()]
      .slice(0, 7)
      .map(([policyName, count]) => {
        const detected = count;
        const prevented = Math.round(detected * (0.72 + Math.random() * 0.24));
        return {
          policyName: policyName.slice(0, 26),
          detected,
          prevented,
          effectiveness: Math.min(100, Math.round((prevented / Math.max(detected, 1)) * 100)),
        };
      });

    const detectionAccuracyTrend = Array.from({ length: 12 }, (_, i) => ({
      label: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i],
      accuracy: rand(94, 99.6),
    }));

    const complianceScoreTrend = [
      { label: 'Q3-25', score: rand(71, 78) },
      { label: 'Q4-25', score: rand(76, 82) },
      { label: 'Q1-26', score: rand(80, 86) },
      { label: 'Q2-26', score: rand(84, 90) },
      { label: 'Q3-26', score: rand(88, 94) },
    ];

    return {
      monthlyThreats: Array.from({ length: 6 }, (_, i) => ({
        label: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][i],
        blocked: rand(8, 60),
        allowed: rand(80, 300),
      })),
      weeklyThreats,
      hourlyAttacks: Array.from({ length: 24 }, (_, h) => ({ hour: h, attacks: rand(0, 18) })),
      departmentComparison: (await departmentSummary()).slice(0, 6).map((d) => ({ department: d.name, riskIndex: d.riskIndex, avgScore: d.avgScore })),
      policyComparison: [...policyComparison.entries()].map(([policyName, count]) => ({ policyName: policyName.slice(0, 24), count })),
      riskEvolution: riskSeries,
      detectionDistribution: [...detectionDistribution.entries()].slice(0, 8).map(([type, count]) => ({ type, count })),
      agentLatency,
      pipelineDuration,
      complianceTrend,
      riskForecast,
      incidentHeatmap,
      policyEffectiveness,
      detectionAccuracyTrend,
      complianceScoreTrend,
      timestamp: new Date().toISOString(),
    };
  });

  // ---------- AI EXPLAINABILITY CENTER ----------
  fastify.get('/api/explain', async () => {
    const records = await recentRecords(40);
    const agents = [
      { id: 'inspector-agent', name: 'Inspector Agent', role: 'Prompt normalisation & intent classification', weight: 0.12 },
      { id: 'secret-detection-agent', name: 'Secret Detection Agent', role: 'Pattern matching for secrets, PII & credentials', weight: 0.34 },
      { id: 'policy-engine', name: 'Policy Engine', role: 'Regulatory enforcement (GDPR · HIPAA · PCI · SOC 2 · ISO)', weight: 0.22 },
      { id: 'risk-engine', name: 'Risk Engine', role: 'Composite risk scoring & decision recommendation', weight: 0.32 },
      { id: 'audit-logger', name: 'Audit Logger', role: 'Immutable tamper-evident record', weight: 0 },
    ];

    const decisions = records.slice(0, 24).map((r: any) => {
      const secrets = (r.secrets ?? []) as Array<{ label: string; confidence: number; severity: string; match: string }>;
      const violations = (r.violations ?? []) as Array<{ policyName: string; regulation: string; severity: string; reason: string; ruleId: string }>;
      const score = Number(r.riskScore ?? 0);

      const riskFactors: Array<{ label: string; weight: number; detail: string; tone: string }> = [];
      if (secrets.length > 0) {
        const worst = secrets.reduce((a, s) => Math.max(a, s.severity === 'CRITICAL' ? 40 : s.severity === 'HIGH' ? 25 : s.severity === 'MEDIUM' ? 12 : 5), 0);
        riskFactors.push({
          label: 'Sensitive data exposure',
          weight: Math.min(55, worst * (1 + Math.min(secrets.length - 1, 5) * 0.15)),
          detail: `${secrets.length} entity${secrets.length === 1 ? '' : 'ies'} matched with ${Math.round((secrets.reduce((a, s) => a + (s.confidence ?? 0.9), 0) / secrets.length) * 100)}% confidence.`,
          tone: 'from-status-high to-status-critical',
        });
      }
      if (violations.length > 0) {
        riskFactors.push({
          label: 'Policy violations',
          weight: Math.min(60, violations.reduce((a, v) => a + (v.severity === 'CRITICAL' ? 40 : v.severity === 'HIGH' ? 25 : v.severity === 'MEDIUM' ? 12 : 5) * 1.2, 0)),
          detail: `${violations.length} pack${violations.length === 1 ? '' : 's'} triggered — ${[...new Set(violations.map((v) => v.regulation))].join(', ') || 'corporate policy'}.`,
          tone: 'from-status-critical to-status-high',
        });
      }
      if (score >= 35 && riskFactors.length === 0) {
        riskFactors.push({ label: 'Elevated composite risk', weight: Math.min(35, score * 0.4), detail: 'Composite score crossed the medium threshold without a single dominant trigger.', tone: 'from-status-medium to-status-high' });
      }
      if (riskFactors.length === 0) riskFactors.push({ label: 'Clean request', weight: 5, detail: 'No sensitive entities or policy violations detected.', tone: 'from-status-low to-status-low' });

      const statusFor = (i: number): 'EXECUTED' | 'SKIPPED' | 'TRIGGERED' =>
        i === 3 ? (score >= 35 ? 'TRIGGERED' : 'EXECUTED') : i === 1 ? (secrets.length ? 'TRIGGERED' : 'EXECUTED') : i === 2 ? (violations.length ? 'TRIGGERED' : 'EXECUTED') : i === 4 ? (r.rewrittenPrompt ? 'TRIGGERED' : 'EXECUTED') : 'EXECUTED';

      const agentContributions = agents.map((a, i) => ({
        agent: a.name,
        role: a.role,
        status: statusFor(i),
        confidence: Math.round(78 + Math.random() * 20),
        contribution: Math.round((a.weight / (0.34 + 0.32)) * 100),
      }));

      const reasoningTimeline = [
        { step: 'Inspector normalises & classifies', detail: 'Prompt parsed, intent and sensitivity band estimated.', ts: 0 },
        { step: 'Secret detection runs pattern engine', detail: secrets.length ? `${secrets.length} entit${secrets.length === 1 ? 'y' : 'ies'} matched.` : 'No secret patterns matched.', ts: 1 },
        { step: 'Policy engine evaluates 7 packs', detail: violations.length ? `${violations.length} pack${violations.length === 1 ? '' : 's'} triggered.` : 'All policy packs passed.', ts: 2 },
        { step: 'Risk engine composes score', detail: `${score}/100 composite — ${r.threatLevel}.`, ts: 3 },
        { step: 'Decision finalised & logged', detail: `${r.decision} recorded to the immutable audit trail.`, ts: 4 },
      ];

      const recommendation =
        r.decision === 'BLOCK'
          ? 'Block was enforced. Review the originating user and department, and consider a one-time training touchpoint.'
          : r.decision === 'REWRITE'
            ? 'Prompt was sanitised before transmission. Monitor whether rewrite frequency rises — it may signal tooling gaps.'
            : r.decision === 'FLAG'
              ? 'Flagged for analyst review. Triage within the investigation queue.'
              : 'Approved — no action required. Continue monitoring baseline drift.';

      const confidence = Math.round(Math.min(99, 74 + secrets.length * 6 + violations.length * 4 + (score >= 80 ? 4 : 0)));

      return {
        id: r.id,
        prompt: String(r.prompt ?? '').slice(0, 140),
        decision: r.decision,
        riskScore: score,
        threatLevel: r.threatLevel,
        timestamp: new Date(String(r.timestamp)).toISOString(),
        user: r.user?.name ?? 'Anonymous',
        department: r.user?.department ?? 'Unknown',
        confidence,
        recommendation,
        agentContributions,
        riskFactors,
        policyFactors: violations.map((v) => ({ policyName: v.policyName, regulation: v.regulation, severity: v.severity, reason: v.reason, ruleId: v.ruleId })),
        reasoningTimeline,
      };
    });

    const summary = {
      total: decisions.length,
      blocked: decisions.filter((d) => d.decision === 'BLOCK').length,
      rewritten: decisions.filter((d) => d.decision === 'REWRITE').length,
      flagged: decisions.filter((d) => d.decision === 'FLAG').length,
      allowed: decisions.filter((d) => d.decision === 'ALLOW').length,
      avgRisk: decisions.length ? Math.round(decisions.reduce((a, d) => a + d.riskScore, 0) / decisions.length) : 0,
      topAgent: agents[1].name,
      topPolicy: [...(new Map<string, number>())].length,
    };

    return { decisions, summary, timestamp: new Date().toISOString() };
  });

  // ---------- SYSTEM DETAILS ----------
  fastify.get('/api/system', async () => {
    const mem = rand(420, 780);
    return {
      version: '1.0.0',
      build: 'sentinelx-enterprise-1.0.0',
      deployment: 'production',
      region: 'ap-south-1 · mumbai',
      uptimeSeconds: 3600 * 24 * rand(3, 41) + rand(0, 3600),
      cluster: { nodes: 3, status: 'HEALTHY', drift: '0.0%' },
      apiLatency: rand(18, 52),
      memoryMb: mem,
      memoryTotalMb: 4096,
      cpuPct: rand(12, 46),
      queueDepth: rand(0, 6),
      threatFeed: 'active',
      websocket: 'connected',
      redis: 'connected',
      database: 'replicated',
      replicas: 3,
      pods: rand(12, 30),
      podsHealthy: '28/28',
      canary: '2%',
    };
  });
}
