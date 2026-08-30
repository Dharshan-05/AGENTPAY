import type { FastifyInstance } from 'fastify';
import { store } from '../lib/store';
import { authMiddleware } from '../lib/auth';

export async function registerAnalyticsRoutes(fastify: FastifyInstance): Promise<void> {
  function getCutoff(period?: string) {
    if (period === 'today') return Date.now() - 86400000;
    if (period === '7d') return Date.now() - 7 * 86400000;
    if (period === '30d') return Date.now() - 30 * 86400000;
    return 0;
  }

  // GET /api/analytics/usage
  fastify.get('/api/analytics/usage', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });
    
    const dbUser = await store.user.findUnique({ where: { id: user.sub } });
    if (!dbUser) return reply.code(404).send({ error: 'User not found' });

    const query = request.query as { period?: string };
    const cutoff = getCutoff(query.period);

    let usages: any[] = await store.usageLedger.findMany({ where: { organizationId: dbUser.organizationId } });
    if (cutoff > 0) usages = usages.filter((u: any) => new Date(u.createdAt).getTime() > cutoff);

    let audits: any[] = await store.auditLog.findMany();
    if (cutoff > 0) audits = audits.filter((a: any) => new Date(a.timestamp).getTime() > cutoff);

    const blocked = audits.filter((a: any) => a.decision === 'BLOCK');
    
    let inputTokens = 0, outputTokens = 0, totalTokens = 0, totalCost = 0;
    usages.forEach((u: any) => {
      inputTokens += (u.inputTokens || 0);
      outputTokens += (u.outputTokens || 0);
      totalTokens += (u.totalTokens || 0);
      totalCost += (u.estimatedCost || 0);
    });

    return {
      totalRequests: audits.length,
      successfulRequests: audits.length - blocked.length,
      blockedRequests: blocked.length,
      failedRequests: 0,
      inputTokens,
      outputTokens,
      totalTokens,
      totalCost,
      avgLatencyMs: 0,
      tokensSaved: 0,
      failoverCount: 0,
      byDay: []
    };
  });

  // GET /api/analytics/employees
  fastify.get('/api/analytics/employees', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });

    return [];
  });

  // GET /api/analytics/models
  fastify.get('/api/analytics/models', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });

    return [];
  });

  // GET /api/analytics/providers
  fastify.get('/api/analytics/providers', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });

    return [];
  });

  // GET /api/analytics/blocked
  fastify.get('/api/analytics/blocked', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });

    return [];
  });

  // GET /api/analytics/gateway-summary
  fastify.get('/api/analytics/gateway-summary', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });

    return {
      requestsToday: 0,
      tokensToday: 0,
      costToday: 0,
      blockedToday: 0,
      piiRedactionsToday: 0,
      secretsBlockedToday: 0,
      injectionBlockedToday: 0,
      tokensSavedToday: 0,
      avgLatencyMs: 0,
      failoversToday: 0,
      budgetUsedPercent: 0,
      weeklyTrend: []
    };
  });
}
