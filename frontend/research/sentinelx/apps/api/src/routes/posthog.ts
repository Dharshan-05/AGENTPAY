import type { FastifyInstance } from "fastify"
import {
  capture,
  identify,
  group,
  healthCheck,
  isPostHogConfigured,
  EVENTS,
} from "../lib/posthog"
import { authMiddleware } from "../lib/auth"

export async function registerPostHogRoutes(app: FastifyInstance): Promise<void> {
  app.get("/api/analytics/health", { preHandler: authMiddleware }, async () => {
    return healthCheck()
  })

  app.post("/api/analytics/capture", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      event: string
      properties?: Record<string, any>
      timestamp?: string
    }

    if (!body.event) {
      return reply.code(400).send({ error: "Event name is required" })
    }

    const user = (request as any).user
    const result = await capture({
      event: body.event,
      distinctId: user?.sub || "anonymous",
      properties: body.properties,
      timestamp: body.timestamp ? new Date(body.timestamp) : undefined,
    })

    if (!result) {
      return reply.code(500).send({ error: "Failed to capture event" })
    }

    return { success: true }
  })

  app.post("/api/analytics/identify", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      userId: string
      traits?: Record<string, any>
    }

    if (!body.userId) {
      return reply.code(400).send({ error: "User ID is required" })
    }

    const result = await identify(body.userId, body.traits ?? {})

    if (!result) {
      return reply.code(500).send({ error: "Failed to identify user" })
    }

    return { success: true }
  })

  app.post("/api/analytics/group", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      groupId: string
      properties?: Record<string, any>
    }

    if (!body.groupId) {
      return reply.code(400).send({ error: "Group ID is required" })
    }

    const result = await group(body.groupId, body.properties ?? {})

    if (!result) {
      return reply.code(500).send({ error: "Failed to identify group" })
    }

    return { success: true }
  })

  app.get("/api/analytics/events", { preHandler: authMiddleware }, async () => {
    return EVENTS
  })

  app.get("/api/analytics/config", { preHandler: authMiddleware }, async () => {
    return {
      configured: isPostHogConfigured(),
      events: EVENTS,
    }
  })

  // Analytics aggregation endpoints for dashboards
  app.get("/api/analytics/summary", { preHandler: authMiddleware }, async () => {

    // Demo data for analytics summary
    return {
      totalUsers: 156,
      activeUsers24h: 89,
      activeUsers7d: 142,
      activeUsers30d: 156,
      organizations: 3,
      events24h: 12450,
      events7d: 87320,
      events30d: 356780,
      avgSessionDuration: 420,
      bounceRate: 12.5,
      topEvents: [
        { event: "prompt_submitted", count: 45230 },
        { event: "prompt_allowed", count: 38920 },
        { event: "dashboard_viewed", count: 24560 },
        { event: "prompt_blocked", count: 12340 },
        { event: "copilot_used", count: 8920 },
        { event: "secret_detected", count: 5670 },
        { event: "incident_created", count: 2340 },
        { event: "policy_triggered", count: 1890 },
        { event: "report_generated", count: 1230 },
      ],
      userGrowth: [
        { date: "2024-01-01", users: 89 },
        { date: "2024-01-08", users: 102 },
        { date: "2024-01-15", users: 118 },
        { date: "2024-01-22", users: 134 },
        { date: "2024-01-29", users: 147 },
        { date: "2024-02-05", users: 156 },
      ],
      riskTrends: [
        { date: "2024-01-01", avgRisk: 28, blocked: 890, allowed: 3120 },
        { date: "2024-01-08", avgRisk: 31, blocked: 945, allowed: 2980 },
        { date: "2024-01-15", avgRisk: 33, blocked: 1020, allowed: 3210 },
        { date: "2024-01-22", avgRisk: 29, blocked: 875, allowed: 3450 },
        { date: "2024-01-29", avgRisk: 27, blocked: 820, allowed: 3680 },
        { date: "2024-02-05", avgRisk: 25, blocked: 790, allowed: 3890 },
      ],
      departmentStats: [
        { department: "Engineering", users: 45, events: 45230, avgRisk: 38, incidents: 23 },
        { department: "Sales", users: 28, events: 18920, avgRisk: 22, incidents: 5 },
        { department: "Marketing", users: 22, events: 12450, avgRisk: 18, incidents: 3 },
        { department: "Finance", users: 18, events: 8920, avgRisk: 15, incidents: 2 },
        { department: "HR", users: 15, events: 5670, avgRisk: 12, incidents: 1 },
        { department: "Legal", users: 12, events: 4320, avgRisk: 10, incidents: 0 },
      ],
      secretTypes: [
        { type: "AWS Access Key", count: 1234, severity: "CRITICAL" },
        { type: "API Token", count: 987, severity: "HIGH" },
        { type: "Database Password", count: 654, severity: "HIGH" },
        { type: "JWT Secret", count: 432, severity: "CRITICAL" },
        { type: "Private Key", count: 321, severity: "CRITICAL" },
        { type: "Credit Card", count: 210, severity: "HIGH" },
        { type: "SSH Key", count: 198, severity: "HIGH" },
        { type: "OAuth Token", count: 156, severity: "MEDIUM" },
      ],
      providerUsage: [
        { provider: "OpenAI", requests: 45230, tokens: 12450000, cost: 2450 },
        { provider: "Anthropic", requests: 18920, tokens: 8920000, cost: 1890 },
        { provider: "Gemini", requests: 12450, tokens: 5670000, cost: 567 },
        { provider: "OpenRouter", requests: 8920, tokens: 3450000, cost: 345 },
        { provider: "Ollama", requests: 3420, tokens: 1230000, cost: 0 },
      ],
    }
  })

  // Funnel analytics
  app.get("/api/analytics/funnels/security", { preHandler: authMiddleware }, async () => {
    return {
      name: "Security Pipeline Funnel",
      steps: [
        { name: "Prompt Submitted", count: 50000, conversion: 100 },
        { name: "Scanned", count: 49850, conversion: 99.7 },
        { name: "Risk Calculated", count: 49500, conversion: 99.0 },
        { name: "Decision Made", count: 49200, conversion: 98.4 },
        { name: "Blocked", count: 12400, conversion: 24.8 },
        { name: "Rewritten", count: 8900, conversion: 17.8 },
        { name: "Allowed", count: 27900, conversion: 55.8 },
      ],
      dropOffs: [
        { from: "Prompt Submitted", to: "Scanned", lost: 150, reason: "Validation failures" },
        { from: "Scanned", to: "Risk Calculated", lost: 350, reason: "Agent timeout" },
        { from: "Risk Calculated", to: "Decision Made", lost: 300, reason: "Policy conflict" },
      ],
      avgDuration: 2.3,
      p95Duration: 5.1,
    }
  })

  // Retention
  app.get("/api/analytics/retention", { preHandler: authMiddleware }, async () => {
    return {
      day1: 68.5,
      day7: 42.3,
      day30: 28.7,
      cohorts: [
        { cohort: "2024-01-01", size: 45, day1: 72, day7: 48, day30: 32 },
        { cohort: "2024-01-08", size: 52, day1: 69, day7: 44, day30: 29 },
        { cohort: "2024-01-15", size: 48, day1: 71, day7: 46, day30: 31 },
        { cohort: "2024-01-22", size: 55, day1: 67, day7: 41, day30: 27 },
        { cohort: "2024-01-29", size: 49, day1: 65, day7: 39, day30: 25 },
      ],
    }
  })

  // Path analysis
  app.get("/api/analytics/paths", { preHandler: authMiddleware }, async () => {
    return {
      topPaths: [
        { path: ["/dashboard", "/scanner", "/incidents"], count: 1240, avgDuration: 420 },
        { path: ["/dashboard", "/executive", "/compliance"], count: 890, avgDuration: 380 },
        { path: ["/login", "/dashboard", "/copilot"], count: 670, avgDuration: 320 },
        { path: ["/dashboard", "/policies", "/settings"], count: 560, avgDuration: 290 },
        { path: ["/scanner", "/explain", "/incidents"], count: 450, avgDuration: 350 },
      ],
      exitPages: [
        { page: "/dashboard", exits: 3420 },
        { page: "/scanner", exits: 2180 },
        { page: "/incidents", exits: 1890 },
        { page: "/copilot", exits: 1560 },
        { page: "/executive", exits: 1230 },
      ],
    }
  })

  // Performance analytics
  app.get("/api/analytics/performance", { preHandler: authMiddleware }, async () => {
    return {
      apiLatency: {
        p50: 45,
        p95: 120,
        p99: 280,
        avg: 62,
      },
      agentLatency: {
        inspector: { p50: 3, p95: 8, p99: 15 },
        secretDetection: { p50: 2, p95: 5, p99: 12 },
        policyEngine: { p50: 1, p95: 3, p99: 8 },
        riskEngine: { p50: 4, p95: 10, p99: 22 },
        adaptiveRisk: { p50: 8, p95: 25, p99: 55 },
        rewriter: { p50: 2, p95: 6, p99: 15 },
        llmAdapter: { p50: 45, p95: 180, p99: 420 },
        auditLogger: { p50: 3, p95: 8, p99: 18 },
      },
      pipelineLatency: {
        avg: 78,
        p50: 65,
        p95: 156,
        p99: 320,
      },
      memoryUsage: {
        heapUsed: 245,
        heapTotal: 380,
        external: 45,
        rss: 420,
      },
      cpuUsage: {
        user: 12.5,
        system: 4.2,
      },
      cacheHitRatio: 0.94,
      redisUsage: {
        connected: true,
        memory: 45.2,
        keys: 12470,
        hits: 892000,
        misses: 56000,
      },
      mongoQueries: {
        avg: 12,
        p50: 8,
        p95: 35,
        p99: 85,
      },
      socketLatency: {
        avg: 2.1,
        p50: 1.5,
        p95: 5.8,
      },
    }
  })

  // Predictions
  app.get("/api/analytics/predictions", { preHandler: authMiddleware }, async () => {
    return {
      threatGrowth: {
        nextWeek: 1240,
        nextMonth: 5200,
        nextQuarter: 15600,
        confidence: 0.87,
        trend: "increasing",
      },
      incidentGrowth: {
        nextWeek: 45,
        nextMonth: 180,
        nextQuarter: 540,
        confidence: 0.82,
        trend: "stable",
      },
      complianceTrend: {
        nextWeek: 97.5,
        nextMonth: 98.2,
        nextQuarter: 98.8,
        confidence: 0.91,
        trend: "improving",
      },
      aiUsage: {
        nextWeek: 52000,
        nextMonth: 215000,
        nextQuarter: 640000,
        confidence: 0.89,
        trend: "increasing",
      },
      monthlyCost: {
        nextMonth: 2890,
        nextQuarter: 8650,
        confidence: 0.85,
        trend: "increasing",
      },
      storageGrowth: {
        nextMonth: 15.2,
        nextQuarter: 45.8,
        confidence: 0.92,
        trend: "stable",
      },
      promptVolume: {
        nextWeek: 52000,
        nextMonth: 220000,
        nextQuarter: 680000,
        confidence: 0.88,
        trend: "increasing",
      },
    }
  })

  // Executive insights
  app.get("/api/analytics/executive", { preHandler: authMiddleware }, async () => {
    return {
      summary: "Threats increased 18% compared to yesterday. API Keys remain the most common leaked secret. Engineering accounts for 64% of critical incidents. Average response time improved from 4.2s → 2.8s. GDPR compliance remained above 98%. AI Recommendation: Enable stricter API key policies for Engineering.",
      topRisks: [
        { risk: "API Key Exposure", count: 1234, trend: "increasing", severity: "HIGH" },
        { risk: "Database Credentials", count: 654, trend: "stable", severity: "HIGH" },
        { risk: "JWT Secret Leakage", count: 432, trend: "decreasing", severity: "CRITICAL" },
        { risk: "Private Key Exposure", count: 321, trend: "stable", severity: "CRITICAL" },
      ],
      securityScore: 87,
      weeklyTrend: {
        threats: "+18%",
        blocked: "+12%",
        rewritten: "+8%",
        incidents: "+5%",
        responseTime: "-34%",
      },
      mostTargetedDepartment: "Engineering",
      mostCommonSecret: "AWS Access Key",
      fastestGrowingThreat: "OAuth Token Theft",
      highestRiskUser: "user_eng_42 (Engineering)",
      complianceHealth: {
        GDPR: 99.2,
        HIPAA: 98.5,
        PCI_DSS: 97.8,
        SOC_2: 98.9,
        ISO_27001: 98.1,
      },
      recommendations: [
        "Enable stricter API key policies for Engineering department",
        "Implement automated secret rotation for database credentials",
        "Add OAuth token monitoring to incident response playbook",
        "Schedule quarterly compliance audit for PCI DSS",
      ],
    }
  })
}