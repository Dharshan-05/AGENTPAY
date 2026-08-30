import type { FastifyInstance } from 'fastify';
import { store } from '../lib/store';
import { authMiddleware } from '../lib/auth';
import { generateApiKey } from '../lib/api-keys';

export async function registerApiKeyRoutes(fastify: FastifyInstance): Promise<void> {
  // Only authenticated admins and users should hit these
  
  // POST /api/admin/api-keys - Admin/User creates a new API key
  fastify.post('/api/admin/api-keys', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    
    // Check RBAC/permissions here depending on SentinelX roles
    // For this implementation, we will allow creating keys for oneself or if admin.
    const body = request.body as { name: string, employeeId?: string, organizationId?: string };
    
    let targetUserId = user.sub;
    let targetOrgId = null;

    if (user.role === 'ADMIN' || user.role === 'SUPER_ADMIN') {
      if (body.employeeId) targetUserId = body.employeeId;
      if (body.organizationId) targetOrgId = body.organizationId;
    } else {
      // Normal employee can only create for themselves
      const dbUser = await store.user.findUnique({ where: { id: user.sub } });
      targetOrgId = dbUser?.organizationId ?? null;
    }

    const { rawSecret, keyPrefix, keyHash, name } = generateApiKey(body.name || 'API Key');

    const newKey = await store.apiKey.create({
      data: {
        name,
        keyPrefix,
        keyHash,
        userId: targetUserId,
        organizationId: targetOrgId,
        status: 'ACTIVE',
      }
    });

    return {
      success: true,
      apiKey: {
        id: newKey.id,
        name: newKey.name,
        prefix: newKey.keyPrefix,
        secret: rawSecret,
        createdAt: newKey.createdAt,
        warning: "This secret will not be shown again. Please copy it now."
      }
    };
  });

  // GET /api/admin/api-keys - List keys
  fastify.get('/api/admin/api-keys', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    
    if (user.role !== 'ADMIN' && user.role !== 'SUPER_ADMIN') {
      return reply.code(403).send({ error: "Forbidden" });
    }

    const query = request.query as { organizationId?: string };
    const where: any = {};
    if (query.organizationId) where.organizationId = query.organizationId;

    const keys = await store.apiKey.findMany({
      where,
      select: {
        id: true,
        name: true,
        keyPrefix: true,
        status: true,
        createdAt: true,
        lastUsedAt: true,
        expiresAt: true,
        userId: true,
        organizationId: true
      },
      orderBy: { createdAt: 'desc' }
    });

    return keys;
  });

  // POST /api/admin/api-keys/:id/revoke - Revoke a key
  fastify.post('/api/admin/api-keys/:id/revoke', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    
    const { id } = request.params as { id: string };

    const apiKey = await store.apiKey.findUnique({ where: { id } });
    if (!apiKey) return reply.code(404).send({ error: "Key not found" });

    // Multi-tenant check
    if (user.role !== 'SUPER_ADMIN') {
      const dbUser = await store.user.findUnique({ where: { id: user.sub } });
      if (!dbUser || (dbUser.organizationId !== apiKey.organizationId && user.sub !== apiKey.userId)) {
        return reply.code(403).send({ error: "Forbidden" });
      }
    }

    await store.apiKey.update({
      where: { id },
      data: {
        status: 'REVOKED',
        revokedAt: new Date()
      }
    });

    // Audit logging
    await store.auditLog.create({
      data: {
        promptHash: 'API_KEY_REVOKED',
        prompt: `Key ${apiKey.keyPrefix} revoked by ${user.sub}`,
        violations: [],
        secrets: [],
        policiesTriggered: [],
        userId: user.sub,
        decision: 'ALLOW',
      }
    });

    return { success: true };
  });

  // POST /api/admin/api-keys/:id/rotate - Rotate a key
  fastify.post('/api/admin/api-keys/:id/rotate', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    
    const { id } = request.params as { id: string };

    const apiKey = await store.apiKey.findUnique({ where: { id } });
    if (!apiKey) return reply.code(404).send({ error: "Key not found" });

    // Multi-tenant check
    if (user.role !== 'SUPER_ADMIN') {
      const dbUser = await store.user.findUnique({ where: { id: user.sub } });
      if (!dbUser || (dbUser.organizationId !== apiKey.organizationId && user.sub !== apiKey.userId)) {
        return reply.code(403).send({ error: "Forbidden" });
      }
    }

    // Revoke old key
    await store.apiKey.update({
      where: { id },
      data: {
        status: 'REVOKED',
        revokedAt: new Date()
      }
    });

    // Generate new key
    const { rawSecret, keyPrefix, keyHash } = generateApiKey(apiKey.name);

    const newKey = await store.apiKey.create({
      data: {
        name: apiKey.name,
        keyPrefix,
        keyHash,
        userId: apiKey.userId,
        organizationId: apiKey.organizationId,
        status: 'ACTIVE',
      }
    });

    // Audit logging
    await store.auditLog.create({
      data: {
        promptHash: 'API_KEY_ROTATED',
        prompt: `Key ${apiKey.keyPrefix} rotated to ${keyPrefix} by ${user.sub}`,
        violations: [],
        secrets: [],
        policiesTriggered: [],
        userId: user.sub,
        decision: 'ALLOW',
      }
    });

    return {
      success: true,
      apiKey: {
        id: newKey.id,
        name: newKey.name,
        prefix: newKey.keyPrefix,
        secret: rawSecret,
        createdAt: newKey.createdAt,
        warning: "This secret will not be shown again. Please copy it now."
      }
    };
  });

  // GET /api/me/api-keys - Employee self-service view
  fastify.get('/api/me/api-keys', async (request, reply) => {
    const user = await authMiddleware(request, reply);
    if (!user) return;
    
    const keys = await store.apiKey.findMany({
      where: { userId: user.sub },
      select: {
        id: true,
        name: true,
        keyPrefix: true,
        status: true,
        createdAt: true,
        lastUsedAt: true,
        expiresAt: true
      },
      orderBy: { createdAt: 'desc' }
    });

    return keys;
  });
}
