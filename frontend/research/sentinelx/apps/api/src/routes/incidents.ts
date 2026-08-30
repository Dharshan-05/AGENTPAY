import type { FastifyInstance } from 'fastify';
import {
  addIncidentEvidence,
  addIncidentNote,
  assignIncident,
  exportIncident,
  getIncident,
  incidentStats,
  listIncidents,
  relatedPromptsFor,
  setIncidentStatus,
  type IncidentStatus,
} from '../lib/incidents';

export async function registerIncidentRoutes(fastify: FastifyInstance): Promise<void> {
  fastify.get('/api/incidents', async (request) => {
    const q = request.query as { severity?: string; status?: string; department?: string };
    return {
      incidents: listIncidents({ severity: q.severity, status: q.status, department: q.department }),
      stats: incidentStats(),
    };
  });

  fastify.get('/api/incidents/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    const inc = getIncident(id);
    if (!inc) return reply.code(404).send({ error: 'Incident not found' });
    return { ...inc, relatedPrompts: relatedPromptsFor(inc) };
  });

  fastify.post('/api/incidents/:id/notes', async (request, reply) => {
    const { id } = request.params as { id: string };
    const body = request.body as { author?: string; body?: string };
    if (!body?.body?.trim()) return reply.code(400).send({ error: 'Note body is required' });
    const inc = addIncidentNote(id, body.author?.trim() || 'Anonymous', body.body.trim());
    if (!inc) return reply.code(404).send({ error: 'Incident not found' });
    return inc;
  });

  fastify.post('/api/incidents/:id/assign', async (request, reply) => {
    const { id } = request.params as { id: string };
    const body = request.body as { owner?: string };
    if (!body?.owner?.trim()) return reply.code(400).send({ error: 'Owner is required' });
    const inc = assignIncident(id, body.owner.trim());
    if (!inc) return reply.code(404).send({ error: 'Incident not found' });
    return inc;
  });

  fastify.post('/api/incidents/:id/status', async (request, reply) => {
    const { id } = request.params as { id: string };
    const body = request.body as { status?: IncidentStatus; actor?: string };
    if (!body?.status || !['TRIAGE', 'INVESTIGATING', 'CONTAINED', 'RESOLVED'].includes(body.status)) {
      return reply.code(400).send({ error: 'Valid status is required' });
    }
    const inc = setIncidentStatus(id, body.status, body.actor?.trim() || 'Analyst');
    if (!inc) return reply.code(404).send({ error: 'Incident not found' });
    return inc;
  });

  fastify.post('/api/incidents/:id/evidence', async (request, reply) => {
    const { id } = request.params as { id: string };
    const body = request.body as { label?: string; value?: string; kind?: 'PROMPT' | 'PATTERN' | 'POLICY' | 'NETWORK' | 'FILE' | 'LOG' };
    if (!body?.label?.trim() || !body?.value?.trim()) return reply.code(400).send({ error: 'Label and value are required' });
    const inc = addIncidentEvidence(id, body.label.trim(), body.value.trim(), body.kind ?? 'FILE');
    if (!inc) return reply.code(404).send({ error: 'Incident not found' });
    return inc;
  });

  fastify.get('/api/incidents/:id/export', async (request, reply) => {
    const { id } = request.params as { id: string };
    const report = exportIncident(id);
    if (!report) return reply.code(404).send({ error: 'Incident not found' });
    return report;
  });
}
