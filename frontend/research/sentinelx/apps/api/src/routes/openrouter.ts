import type { FastifyInstance } from 'fastify';
import { getOpenRouterHealthCheckExport, getOpenRouterMetricsExport, resetOpenRouterMetricsExport } from '../llm/providers';

export async function registerOpenRouterRoutes(fastify: FastifyInstance): Promise<void> {
  fastify.get('/api/openrouter/health', async () => {
    return getOpenRouterHealthCheckExport();
  });

  fastify.get('/api/openrouter/metrics', async () => {
    return getOpenRouterMetricsExport();
  });

  fastify.post('/api/openrouter/metrics/reset', async () => {
    resetOpenRouterMetricsExport();
    return { success: true };
  });
}