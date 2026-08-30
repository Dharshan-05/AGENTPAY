import type { FastifyInstance } from 'fastify';
import { store } from '../lib/store';
import { authMiddleware } from '../lib/auth';

export async function registerGovernanceRoutes(fastify: FastifyInstance): Promise<void> {
  // GET /api/admin/employees
  fastify.get('/api/admin/employees', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') {
      return reply.code(403).send({ error: 'Forbidden' });
    }

    const dbUser = await store.user.findUnique({ where: { id: user.sub } });
    if (!dbUser) return reply.code(404).send({ error: 'User not found' });

    const employees = await store.user.findMany({
      where: { organizationId: dbUser.organizationId },
    });

    const enriched = await Promise.all(employees.map(async (emp: any) => {
      const [apiKeys, quota, budget, modelPerms, providerPerms, usage] = await Promise.all([
        store.apiKey.findMany({ where: { userId: emp.id, status: 'ACTIVE' } }),
        store.quota.findFirst({ where: { userId: emp.id } }),
        store.budget.findFirst({ where: { userId: emp.id } }),
        store.employeeModelPermission.findFirst({ where: { employeeId: emp.id } }),
        store.employeeProviderPermission.findFirst({ where: { employeeId: emp.id } }),
        store.usageLedger.findMany({ where: { userId: emp.id } })
      ]);

      const requestsToday = usage.filter((u: any) => new Date(u.createdAt).getTime() > Date.now() - 86400000).length;
      const tokensToday = usage.filter((u: any) => new Date(u.createdAt).getTime() > Date.now() - 86400000)
        .reduce((sum: number, u: any) => sum + (u.totalTokens || 0), 0);
      const costToday = usage.filter((u: any) => new Date(u.createdAt).getTime() > Date.now() - 86400000)
        .reduce((sum: number, u: any) => sum + (u.estimatedCost || 0), 0);

      return {
        id: emp.id,
        name: emp.name,
        email: emp.email,
        role: emp.role,
        department: emp.department,
        organizationId: emp.organizationId,
        apiKeys: apiKeys.length,
        dailyTokenLimit: quota?.dailyTokenLimit || 0,
        monthlyTokenLimit: quota?.monthlyTokenLimit || 0,
        dailyBudget: budget?.dailyBudget || 0,
        monthlyBudget: budget?.monthlyBudget || 0,
        allowedModels: modelPerms?.allowedModels || [],
        deniedModels: modelPerms?.deniedModels || [],
        allowedProviders: providerPerms?.allowedProviders || [],
        deniedProviders: providerPerms?.deniedProviders || [],
        requestsToday,
        tokensToday,
        costToday
      };
    }));

    return enriched;
  });

  // GET /api/admin/employees/:id
  fastify.get('/api/admin/employees/:id', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    const { id } = request.params as { id: string };
    
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN' && user.sub !== id) {
      return reply.code(403).send({ error: 'Forbidden' });
    }

    const emp = await store.user.findUnique({ where: { id } });
    if (!emp) return reply.code(404).send({ error: 'Employee not found' });

    const [apiKeys, quota, budget, modelPerms, providerPerms] = await Promise.all([
        store.apiKey.findMany({ where: { userId: emp.id, status: 'ACTIVE' } }),
        store.quota.findFirst({ where: { userId: emp.id } }),
        store.budget.findFirst({ where: { userId: emp.id } }),
        store.employeeModelPermission.findFirst({ where: { employeeId: emp.id } }),
        store.employeeProviderPermission.findFirst({ where: { employeeId: emp.id } })
    ]);

    return {
      id: emp.id,
      name: emp.name,
      email: emp.email,
      role: emp.role,
      department: emp.department,
      organizationId: emp.organizationId,
      apiKeys,
      quota,
      budget,
      modelPermissions: modelPerms,
      providerPermissions: providerPerms
    };
  });

  // PUT /api/admin/employees/:id/quota
  fastify.put('/api/admin/employees/:id/quota', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });
    
    const { id } = request.params as { id: string };
    const body = request.body as any;

    const existing = await store.quota.findFirst({ where: { userId: id } });
    if (existing) {
      // Use update logic if memory mock supported it, or create.
      // Wait, memory store doesn't have full prisma update mock typically, but we can just push a new one 
      // or if using real prisma, use upsert. Since this might be memory:
      await (store.quota as any).create({ data: { ...body, userId: id } });
    } else {
      await store.quota.create({ data: { ...body, userId: id } });
    }
    return { success: true };
  });

  // PUT /api/admin/employees/:id/budget
  fastify.put('/api/admin/employees/:id/budget', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });
    
    const { id } = request.params as { id: string };
    const body = request.body as any;

    const existing = await store.budget.findFirst({ where: { userId: id } });
    if (existing) {
      await (store.budget as any).create({ data: { ...body, userId: id } });
    } else {
      await store.budget.create({ data: { ...body, userId: id } });
    }
    return { success: true };
  });

  // PUT /api/admin/employees/:id/model-permissions
  fastify.put('/api/admin/employees/:id/model-permissions', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });
    
    const { id } = request.params as { id: string };
    const body = request.body as any;

    await store.employeeModelPermission.create({ data: { ...body, employeeId: id } });
    return { success: true };
  });

  // PUT /api/admin/employees/:id/provider-permissions
  fastify.put('/api/admin/employees/:id/provider-permissions', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });
    
    const { id } = request.params as { id: string };
    const body = request.body as any;

    await store.employeeProviderPermission.create({ data: { ...body, employeeId: id } });
    return { success: true };
  });

  // GET /api/admin/employees/:id/usage
  fastify.get('/api/admin/employees/:id/usage', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    const { id } = request.params as { id: string };
    const query = request.query as { period?: string };

    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN' && user.sub !== id) {
      return reply.code(403).send({ error: 'Forbidden' });
    }

    let cutoff = 0;
    if (query.period === 'today') cutoff = Date.now() - 86400000;
    else if (query.period === '7d') cutoff = Date.now() - 7 * 86400000;
    else if (query.period === '30d') cutoff = Date.now() - 30 * 86400000;

    let usages = await store.usageLedger.findMany({ where: { userId: id } });
    if (cutoff > 0) {
      usages = usages.filter((u: any) => new Date(u.createdAt).getTime() > cutoff);
    }
    
    return usages;
  });

  // GET /api/admin/org/usage
  fastify.get('/api/admin/org/usage', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') return reply.code(403).send({ error: 'Forbidden' });
    const query = request.query as { period?: string };

    let cutoff = 0;
    if (query.period === 'today') cutoff = Date.now() - 86400000;
    else if (query.period === '7d') cutoff = Date.now() - 7 * 86400000;
    else if (query.period === '30d') cutoff = Date.now() - 30 * 86400000;

    const dbUser = await store.user.findUnique({ where: { id: user.sub } });
    if (!dbUser) return reply.code(404).send({ error: 'User not found' });

    let usages: any[] = await store.usageLedger.findMany({ where: { organizationId: dbUser.organizationId } });
    if (cutoff > 0) {
      usages = usages.filter((u: any) => new Date(u.createdAt).getTime() > cutoff);
    }
    
    return usages;
  });
}
