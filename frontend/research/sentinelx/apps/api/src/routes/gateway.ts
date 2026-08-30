/**
 * PHASE 3 — OpenAI-Compatible AI Gateway
 * POST /v1/chat/completions
 *
 * Full enforcement pipeline:
 * API Key Auth → Rate Limit → Quota → Budget → Model Permission →
 * Security Scan → Policy → Optimization → Model Router → Provider → Response
 */
import crypto from 'crypto';
import type { FastifyInstance } from 'fastify';
import { apiKeyAuthMiddleware } from '../lib/auth';
import { store } from '../lib/store';
import { enforceGatewayPolicy, releaseConcurrency, ensureStoreExtensions } from '../lib/enforcement';
import { enforceSecurityPolicy, optimizePrompt } from '../lib/security';
import { resolveAndRouteModel, executeWithFailover } from '../lib/model-router';
import { calculateEstimatedCost } from '../lib/model-registry';
import type { ChatMessage } from '../llm/providers';
import { estimateTokens } from '../llm/tokens';

// ── Error codes ────────────────────────────────────────────────────────────────
export const GW_ERRORS = {
  AUTHENTICATION_REQUIRED:  { code: 'AUTHENTICATION_REQUIRED',  status: 401 },
  INVALID_API_KEY:          { code: 'INVALID_API_KEY',          status: 401 },
  MODEL_NOT_ALLOWED:        { code: 'MODEL_NOT_ALLOWED',        status: 403 },
  PROVIDER_NOT_ALLOWED:     { code: 'PROVIDER_NOT_ALLOWED',     status: 403 },
  POLICY_BLOCKED:           { code: 'POLICY_BLOCKED',           status: 403 },
  RATE_LIMIT_EXCEEDED:      { code: 'RATE_LIMIT_EXCEEDED',      status: 429 },
  DAILY_TOKEN_LIMIT_EXCEEDED:   { code: 'DAILY_TOKEN_LIMIT_EXCEEDED',   status: 429 },
  MONTHLY_TOKEN_LIMIT_EXCEEDED: { code: 'MONTHLY_TOKEN_LIMIT_EXCEEDED', status: 429 },
  REQUEST_TOKEN_LIMIT_EXCEEDED: { code: 'REQUEST_TOKEN_LIMIT_EXCEEDED', status: 400 },
  DAILY_REQUEST_LIMIT_EXCEEDED: { code: 'DAILY_REQUEST_LIMIT_EXCEEDED', status: 429 },
  MONTHLY_REQUEST_LIMIT_EXCEEDED:{ code: 'MONTHLY_REQUEST_LIMIT_EXCEEDED', status: 429 },
  CONCURRENT_LIMIT_EXCEEDED:    { code: 'CONCURRENT_LIMIT_EXCEEDED',    status: 429 },
  DAILY_BUDGET_EXCEEDED:    { code: 'DAILY_BUDGET_EXCEEDED',    status: 429 },
  MONTHLY_BUDGET_EXCEEDED:  { code: 'MONTHLY_BUDGET_EXCEEDED',  status: 429 },
  PROVIDER_TIMEOUT:         { code: 'PROVIDER_TIMEOUT',         status: 504 },
  ALL_PROVIDERS_FAILED:     { code: 'ALL_PROVIDERS_FAILED',     status: 503 },
} as const;

type GwErrorKey = keyof typeof GW_ERRORS;

function gwError(key: GwErrorKey, requestId: string, extra?: string) {
  const { code, status } = GW_ERRORS[key];
  return { code: status, body: { error: { code, message: extra ?? code, requestId } } };
}

// Model routing is now handled by lib/model-router.ts

// ── Security pipeline (Phase 3: basic PII/secret detection) ──────────────────
// Security and Prompt optimization are now handled by lib/security.ts

// ── OpenAI-compatible response shaper ─────────────────────────────────────────
function toOpenAIResponse(requestId: string, model: string, content: string, usage: { promptTokens: number; completionTokens: number }) {
  return {
    id: `chatcmpl-${requestId}`,
    object: 'chat.completion',
    created: Math.floor(Date.now() / 1000),
    model,
    choices: [
      {
        index: 0,
        message: { role: 'assistant', content },
        finish_reason: 'stop',
      },
    ],
    usage: {
      prompt_tokens:     usage.promptTokens,
      completion_tokens: usage.completionTokens,
      total_tokens:      usage.promptTokens + usage.completionTokens,
    },
  };
}

export async function registerGatewayRoutes(fastify: FastifyInstance): Promise<void> {
  await ensureStoreExtensions();

  fastify.post('/v1/chat/completions', async (request, reply) => {
    const requestId = crypto.randomUUID();
    reply.header('X-SentinelX-Request-ID', requestId);

    // ── STEP 1: API Key Authentication ──────────────────────────────────────
    await apiKeyAuthMiddleware(request, reply);
    if (reply.sent) return; // Auth rejected — response already sent

    const auth = (request as any).gatewayAuth as {
      apiKeyId: string; userId: string; organizationId: string | null; scopes: any;
    };

    // ── STEP 2: Parse request body ──────────────────────────────────────────
    const body = (request.body ?? {}) as {
      model?: string;
      messages?: Array<{ role: string; content: string }>;
      temperature?: number;
      max_tokens?: number;
      stream?: boolean;
    };

    const rawMessages = (body.messages ?? []) as ChatMessage[];
    if (!rawMessages.length) {
      return reply.code(400).send({ error: { code: 'INVALID_REQUEST', message: 'messages array is required', requestId } });
    }

    // Validate roles
    for (const m of rawMessages) {
      if (!['system', 'user', 'assistant'].includes(m.role)) {
        return reply.code(400).send({ error: { code: 'INVALID_REQUEST', message: `Invalid role: ${m.role}`, requestId } });
      }
    }

    // ── STEP 3: Estimate request token size ─────────────────────────────────
    const estimatedInputTokens = estimateTokens(rawMessages);

    // ── STEP 4: Quota, Rate Limit, and Budget Enforcement ───────────────────
    const enforcement = await enforceGatewayPolicy({
      userId: auth.userId,
      organizationId: auth.organizationId,
      apiKeyId: auth.apiKeyId,
      estimatedInputTokens,
      requestId,
    });

    if (!enforcement.allowed) {
      // Create AuditLog for rejected request
      await store.auditLog.create({
        data: {
          userId: auth.userId,
          promptHash: '',
          prompt: '[REJECTED - ' + enforcement.code + ']',
          violations: [],
          secrets: [],
          policiesTriggered: [{ policyName: 'Resource Enforcement', action: 'BLOCK' }],
          decision: 'BLOCK',
          riskScore: 0,
          threatLevel: 'LOW',
          llmProvider: null,
          llmModel: null,
          latencyMs: 0,
        },
      }).catch(() => {});

      const err = gwError(enforcement.code as GwErrorKey, requestId, enforcement.message);
      if (enforcement.retryAfter) reply.header('Retry-After', enforcement.retryAfter);
      return reply.code(err.code).send(err.body);
    }

    const concurrencyKey = enforcement.concurrencyKey;

    try {
      // ── STEP 4.1: Resolve model + provider ────────────────────────────────────
      const routingDecision = await resolveAndRouteModel(body.model ?? 'sentinel-auto', auth.userId, auth.organizationId, rawMessages);
      if (!routingDecision.allowed) {
        const err = gwError(routingDecision.errorCode as GwErrorKey ?? 'MODEL_NOT_ALLOWED', requestId, routingDecision.errorMessage);
        return reply.code(err.code).send(err.body);
      }

      // ── STEP 5: Security scan pipeline ─────────────────────────────────────
      const security = enforceSecurityPolicy(rawMessages);

      if (security.decision === 'BLOCK') {
        const userContent = rawMessages.map(m => m.content).join('\n');
        const threatLevel = security.riskScore >= 80 ? 'CRITICAL' : security.riskScore >= 50 ? 'HIGH' : 'MEDIUM';

        await store.auditLog.create({
          data: {
            userId: auth.userId,
            promptHash: crypto.createHash('sha256').update(userContent).digest('hex'),
            prompt: '[REDACTED - contained secrets/injection]',
            violations: security.findings.map((f) => ({ category: f.type.toLowerCase(), label: f.label })),
            secrets: security.findings.filter(f => f.type === 'SECRET').map(f => ({ label: f.label })),
            policiesTriggered: [{ policyName: 'Security Detection', action: 'BLOCK' }],
            decision: 'BLOCK',
            riskScore: security.riskScore,
            threatLevel,
            llmProvider: null,
            llmModel: null,
            latencyMs: 0,
          },
        }).catch(() => {});

        reply.header('X-SentinelX-Decision', 'BLOCK');
        reply.header('X-SentinelX-Risk-Score', String(security.riskScore));
        reply.header('X-SentinelX-Threat-Level', threatLevel);

        return reply.code(403).send({
          error: {
            code: 'POLICY_BLOCKED',
            message: 'Request blocked by SentinelX security policy.',
            requestId,
          },
          sentinelx: {
            decision: 'BLOCK',
            riskScore: security.riskScore,
            threatLevel,
            providerCalls: 0,
            threats: security.findings.map(f => ({
              type: f.type,
              label: f.label,
              severity: f.severity,
            })),
          },
        });
      }

      // ── STEP 6: Prompt optimization ─────────────────────────────────────────
      const optimization = optimizePrompt(security.sanitizedMessages);

      reply.header('X-SentinelX-Security-Decision', security.decision);
      reply.header('X-SentinelX-Risk-Score', security.riskScore);

    // ── STEP 7: Route to provider and call LLM ──────────────────────────────
    const startMs = Date.now();
    let result;
    try {
      result = await executeWithFailover(routingDecision.modelQueue, routingDecision.routingReason, {
        messages: optimization.messages,
        temperature: body.temperature ?? 0.7,
        maxTokens: body.max_tokens ?? 1024,
      });
    } catch (err: any) {
      const userContent = rawMessages.map(m => m.content).join('\n');
      const promptHash = crypto.createHash('sha256').update(userContent).digest('hex');

      // Persist failed request audit
      await store.auditLog.create({
        data: {
          userId: auth.userId,
          promptHash,
          prompt: '[PROVIDER ERROR]',
          violations: [],
          secrets: [],
          policiesTriggered: [],
          decision: 'ALLOW',
          riskScore: 0,
          threatLevel: 'LOW',
          llmProvider: routingDecision.modelQueue[0],
          llmModel: routingDecision.modelQueue[0],
          latencyMs: Date.now() - startMs,
        },
      }).catch(() => {});

      return reply.code(503).send({
        error: { code: 'ALL_PROVIDERS_FAILED', message: err?.message ?? 'Provider unavailable', requestId },
      });
    }

    const latencyMs = Date.now() - startMs;
    const userContent = rawMessages.map(m => m.content).join('\n');
    const promptHash = crypto.createHash('sha256').update(userContent).digest('hex');

    // Persist AIRequest record
    const aiRequest = await store.aiRequest.create({
      data: {
        userId: auth.userId,
        organizationId: auth.organizationId,
        apiKeyId: auth.apiKeyId,
        model: result.model,
        provider: result.provider,
        promptHash,
        status: 'SUCCESS',
        latencyMs,
      },
    }).catch(() => null);

    // Persist UsageLedger
    if (aiRequest) {
      const isSimulated = result.simulated;
      const reportedInput = result.promptTokens;
      const reportedOutput = result.completionTokens;
      const actualCost = isSimulated ? null : calculateEstimatedCost(result.model, reportedInput, reportedOutput);

      await store.usageLedger.create({
        data: {
          requestId: aiRequest.id,
          userId: auth.userId,
          organizationId: auth.organizationId,
          apiKeyId: auth.apiKeyId,
          model: result.model,
          provider: result.provider,
          inputTokens: reportedInput,
          outputTokens: reportedOutput,
          totalTokens: reportedInput + reportedOutput,
          estimatedCost: actualCost ?? 0,
          actualCost: actualCost,
          latencyMs,
          status: 'SUCCESS',
        },
      }).catch(() => {});
    }

    // Persist AuditLog
    await store.auditLog.create({
      data: {
        userId: auth.userId,
        promptHash,
        prompt: security.decision === 'REDACT' ? '[PII REDACTED]' : userContent.slice(0, 500),
        rewrittenPrompt: security.decision === 'REDACT' ? optimization.messages.map((m) => m.content).join('\n').slice(0, 500) : undefined,
        violations: security.findings.map((f) => ({ category: f.type.toLowerCase(), label: f.label })),
        secrets: [],
        policiesTriggered: security.decision === 'REDACT' ? [{ policyName: 'PII Redaction', action: 'REDACT' }] : [],
        decision: security.decision,
        riskScore: security.riskScore,
        threatLevel: security.riskScore >= 80 ? 'CRITICAL' : security.riskScore >= 50 ? 'HIGH' : security.riskScore >= 20 ? 'MEDIUM' : 'LOW',
        llmProvider: result.provider,
        llmModel: result.model,
        latencyMs,
        agentTrace: {
          tokensSaved: optimization.tokensSaved,
          originalTokens: optimization.originalTokens,
          optimizedTokens: optimization.optimizedTokens,
          optimizationRatio: optimization.reductionPercentage,
          simulated: result.simulated,
          attemptCount: result.attemptCount,
          failoverUsed: result.failoverOccurred,
          routingReason: result.routingReason,
          requestedModel: body.model ?? 'sentinel-auto',
          requestId,
          apiKeyId: auth.apiKeyId,
        },
      },
    }).catch(() => {});

    // ── STEP 9: Return OpenAI-compatible response ────────────────────────────
    return toOpenAIResponse(requestId, result.model, result.text, {
      promptTokens: result.promptTokens,
      completionTokens: result.completionTokens,
    });
    } finally {
      await releaseConcurrency(concurrencyKey);
    }
  });

  // ── Gateway status endpoint ─────────────────────────────────────────────────
  fastify.get('/v1/models', async () => ({
    object: 'list',
    data: [
      { id: 'sentinel-auto',    object: 'model', created: 1700000000, owned_by: 'sentinelx' },
      { id: 'gpt-4o-mini',      object: 'model', created: 1700000000, owned_by: 'openai' },
      { id: 'gpt-4o',           object: 'model', created: 1700000000, owned_by: 'openai' },
      { id: 'claude-3-5-haiku', object: 'model', created: 1700000000, owned_by: 'anthropic' },
      { id: 'gemini-flash',     object: 'model', created: 1700000000, owned_by: 'google' },
    ],
  }));

  // ── /v1/analyze: Pure security analysis, no LLM call ────────────────────────
  fastify.post('/v1/analyze', async (request, reply) => {
    const requestId = crypto.randomUUID();
    reply.header('X-SentinelX-Request-ID', requestId);

    await apiKeyAuthMiddleware(request, reply);
    if (reply.sent) return;

    const body = (request.body ?? {}) as { messages?: Array<{ role: string; content: string }> };
    const messages = (body.messages ?? []) as ChatMessage[];

    if (!messages.length) {
      return reply.code(400).send({ error: { code: 'INVALID_REQUEST', message: 'messages array is required', requestId } });
    }

    const security = enforceSecurityPolicy(messages);
    const threatLevel =
      security.riskScore >= 80 ? 'CRITICAL' :
      security.riskScore >= 50 ? 'HIGH' :
      security.riskScore >= 20 ? 'MEDIUM' : 'LOW';

    const threats = security.findings.map(f => ({
      type: f.type,
      label: f.label,
      severity: f.severity,
      action: f.action,
    }));

    reply.header('X-SentinelX-Decision', security.decision);
    reply.header('X-SentinelX-Risk-Score', String(security.riskScore));
    reply.header('X-SentinelX-Threat-Level', threatLevel);

    return reply.code(200).send({
      requestId,
      decision: security.decision,
      riskScore: security.riskScore,
      threatLevel,
      providerCalls: 0,
      threats,
      originalTokenEstimate: security.originalTokenEstimate,
      sanitizedTokenEstimate: security.sanitizedTokenEstimate,
      ...(security.decision === 'REDACT' && {
        sanitizedMessages: security.sanitizedMessages,
      }),
    });
  });
}
