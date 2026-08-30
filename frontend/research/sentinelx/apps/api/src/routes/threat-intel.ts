import type { FastifyInstance } from 'fastify';

export interface ThreatAdvisory {
  id: string;
  source: 'CISA' | 'MITRE' | 'OWASP' | 'GitHub' | 'OpenAI' | 'Microsoft';
  title: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  cvss: number;
  published: string;
  affected: string;
  status: 'ACTIVE' | 'WATCHING' | 'RESOLVED';
  cve?: string;
  tactic?: string;
  mitigation: string;
  relevance: string;
}

const DAY = 3600 * 1000;

function daysAgo(n: number): string {
  return new Date(Date.now() - n * DAY).toISOString().slice(0, 10);
}

const FEED: ThreatAdvisory[] = [
  {
    id: 'CISA-2026-084',
    source: 'CISA',
    title: 'Prompt injection in enterprise AI copilots bypassing guardrails',
    description: 'Adversaries are weaponizing indirect prompt injection via pasted documents to disable content filters and exfiltrate conversation context from enterprise copilot deployments.',
    severity: 'CRITICAL',
    cvss: 9.1,
    published: daysAgo(2),
    affected: 'All copilot deployments with document-paste support',
    status: 'ACTIVE',
    cve: 'CVE-2026-4137',
    mitigation: 'Enable gateway-level context sanitization and block raw document paste for privileged workspaces.',
    relevance: 'Directly matches SentinelX REWRITE + BLOCK decisions',
  },
  {
    id: 'MITRE-T1555',
    source: 'MITRE',
    title: 'T1555 — Credentials from Password Stores (LLM extension)',
    description: 'Threat actors now instruct models to recall credentials cached in browser extensions and session stores via natural-language social engineering within chat context.',
    severity: 'HIGH',
    cvss: 8.2,
    published: daysAgo(5),
    affected: 'Workstations with credential-manager extensions',
    status: 'ACTIVE',
    tactic: 'Credential Access',
    mitigation: 'Block secret-category prompts and enforce auto-rewrite for credential patterns.',
    relevance: 'Matches credential-pattern detections in SentinelX ruleset',
  },
  {
    id: 'OWASP-LLM-01',
    source: 'OWASP',
    title: 'OWASP Top 10 for LLM Apps — LLM01 Prompt Injection (2026 update)',
    description: 'Updated guidance: prompt injection is now present in 41% of enterprise AI incidents. Includes new defense matrix for gateway-level policy enforcement.',
    severity: 'CRITICAL',
    cvss: 8.8,
    published: daysAgo(9),
    affected: 'All LLM application stacks',
    status: 'WATCHING',
    mitigation: 'Deploy layered policy engine with regex + policy-pack evaluation before model egress.',
    relevance: 'Mirrors SentinelX 8-agent pipeline architecture',
  },
  {
    id: 'GHSA-4f5h-9x3q',
    source: 'GitHub',
    title: 'GHSA-4f5h-9x3q — Dependency confusion in python tooling used by AI pipelines',
    description: 'A popular prompt-engineering utility published a malicious version to a public registry; models embedding it may route prompts to attacker-controlled endpoints.',
    severity: 'HIGH',
    cvss: 7.9,
    published: daysAgo(1),
    affected: 'Python AI pipelines pulling unpinned dependencies',
    status: 'ACTIVE',
    cve: 'CVE-2026-29914',
    mitigation: 'Pin dependencies and scan lockfiles for registry mismatches.',
    relevance: 'Relevant to Engineering department risk',
  },
  {
    id: 'OPENAI-2026-03',
    source: 'OpenAI',
    title: 'Shadow API key rotation advisory — leaked keys on public code hosts',
    description: 'OpenAI rotated 3,400+ leaked keys found on public repositories this week. Organizations using legacy key formats are exposed to quota theft.',
    severity: 'HIGH',
    cvss: 7.5,
    published: daysAgo(3),
    affected: 'Any app using sk-… prefixed keys',
    status: 'WATCHING',
    mitigation: 'Rotate keys, enable project-scoped keys, and block legacy formats at the gateway.',
    relevance: 'Matches SentinelX OpenAI API key detection rule',
  },
  {
    id: 'MSFT-2026-112',
    source: 'Microsoft',
    title: 'Copilot tenant isolation gap in shared workspaces',
    description: 'Microsoft disclosed a configuration where cross-tenant data could surface in shared Copilot threads if sensitivity labels are not enforced at the gateway.',
    severity: 'MEDIUM',
    cvss: 6.4,
    published: daysAgo(7),
    affected: 'M365 Copilot tenants with unlabeled shared sites',
    status: 'RESOLVED',
    mitigation: 'Enforce sensitivity labels and review shared-site permissions.',
    relevance: 'Relevant to Legal and HR departments',
  },
  {
    id: 'MITRE-T1530',
    source: 'MITRE',
    title: 'T1530 — Data from Cloud Storage (via AI data connectors)',
    description: 'Adversaries abuse AI data connectors with over-permissioned service accounts to query documents stored in cloud buckets.',
    severity: 'HIGH',
    cvss: 7.8,
    published: daysAgo(12),
    affected: 'Connectors with broad bucket permissions',
    status: 'WATCHING',
    tactic: 'Collection',
    mitigation: 'Least-privilege connector scopes and egress monitoring.',
    relevance: 'Related to Finance document exfiltration incident',
  },
  {
    id: 'OWASP-LLM-06',
    source: 'OWASP',
    title: 'OWASP LLM06 — Excessive Agency: tool-calling autonomy',
    description: 'Models with tool-calling permissions can trigger external actions; recommended maximum-interaction policies and human-in-the-loop gates for destructive tools.',
    severity: 'MEDIUM',
    cvss: 6.0,
    published: daysAgo(15),
    affected: 'Agentic workflows with tool access',
    status: 'WATCHING',
    mitigation: 'Cap autonomous tool calls and require approval for sensitive actions.',
    relevance: 'Informs policy-pack recommendations',
  },
];

export async function registerThreatIntelRoutes(fastify: FastifyInstance): Promise<void> {
  fastify.get('/api/threat-intel', async () => {
    const sources = ['CISA', 'MITRE', 'OWASP', 'GitHub', 'OpenAI', 'Microsoft'];
    const active = FEED.filter((a) => a.status === 'ACTIVE').length;
    const critical = FEED.filter((a) => a.severity === 'CRITICAL').length;
    return {
      feed: FEED,
      sources,
      stats: {
        total: FEED.length,
        active,
        critical,
        avgCvss: Math.round((FEED.reduce((a, x) => a + x.cvss, 0) / FEED.length) * 10) / 10,
      },
      lastSynced: new Date().toISOString(),
    };
  });

  fastify.get('/api/threat-intel/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    const advisory = FEED.find((a) => a.id === id);
    if (!advisory) return reply.code(404).send({ error: 'Advisory not found' });
    return advisory;
  });
}
