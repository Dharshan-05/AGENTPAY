import OpenAI from 'openai';
import { estimateTokens, estimateCost } from './tokens';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface CompleteParams {
  messages: ChatMessage[];
  temperature?: number;
  maxTokens?: number;
  jsonMode?: boolean;
}

export interface OpenRouterModelConfig {
  name: string;
  priority: number;
}

export interface CompleteResult {
  text: string;
  model: string;
  provider: string;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  estimatedCostUsd: number;
  latencyMs: number;
  simulated: boolean;
  attemptNumber: number;
  failoverOccurred: boolean;
  failoverReason?: string;
}

export interface AttemptLog {
  attemptNumber: number;
  model: string;
  status: 'success' | 'failed';
  latencyMs: number;
  reason?: string;
  errorCode?: string;
}

export interface OpenRouterMetrics {
  primarySuccessRate: number;
  fallbackSuccessRate: number;
  secondarySuccessRate: number;
  averageLatencyMs: number;
  failureReasons: Record<string, number>;
  timeoutCount: number;
  rateLimitCount: number;
  providerErrorCount: number;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
}

export interface HealthCheckResult {
  configuredModels: string[];
  currentDefault: string;
  apiConnectivity: boolean;
  providerStatus: string;
  lastSuccessfulModel: string | null;
  successRates: {
    primary: number;
    fallback: number;
    secondary: number;
  };
  averageLatencyMs: number;
}

const FAILOVER_TRIGGER_CODES = new Set([
  429, 500, 502, 503, 504,
]);

const FAILOVER_TRIGGER_MESSAGES = [
  'timeout',
  'connection refused',
  'dns',
  'provider unavailable',
  'rate limit',
  'gateway timeout',
  'internal provider error',
  'invalid upstream response',
  'abort',
  'socket timeout',
];

const DO_NOT_FAILOVER_CODES = new Set([400, 401, 403]);
const DO_NOT_FAILOVER_MESSAGES = [
  'invalid prompt',
  'invalid json',
  'bad request',
  'authentication',
  'unauthorized',
  'invalid api key',
  'content policy',
  'exceeds limit',
  'validation',
];

const MAX_ATTEMPTS_PER_MODEL = 1;
const REQUEST_TIMEOUT_MS = 30000;

const metrics: OpenRouterMetrics = {
  primarySuccessRate: 0,
  fallbackSuccessRate: 0,
  secondarySuccessRate: 0,
  averageLatencyMs: 0,
  failureReasons: {},
  timeoutCount: 0,
  rateLimitCount: 0,
  providerErrorCount: 0,
  totalRequests: 0,
  successfulRequests: 0,
  failedRequests: 0,
};

const attemptLogs: AttemptLog[] = [];
let lastSuccessfulModel: string | null = null;
let apiConnectivity = false;

function getModelConfigs(): OpenRouterModelConfig[] {
  const defaultModel = process.env.OPENROUTER_DEFAULT_MODEL ?? 'nvidia/nemotron-3-ultra';
  const fallbackModel = process.env.OPENROUTER_FALLBACK_MODEL ?? 'nvidia/nemotron-3-super';
  const secondaryModel = process.env.OPENROUTER_SECONDARY_MODEL ?? 'openai/gpt-oss-20b';

  return [
    { name: defaultModel, priority: 1 },
    { name: fallbackModel, priority: 2 },
    { name: secondaryModel, priority: 3 },
  ];
}

function determineFailover(error: unknown, _attemptNumber: number): { shouldFailover: boolean; reason: string; errorCode?: string } {
  if (error instanceof OpenAI.APIError) {
    const status = error.status;
    if (status && FAILOVER_TRIGGER_CODES.has(status)) {
      return { shouldFailover: true, reason: `HTTP ${status}`, errorCode: String(status) };
    }
    if (status && DO_NOT_FAILOVER_CODES.has(status)) {
      return { shouldFailover: false, reason: `HTTP ${status} (non-failover)`, errorCode: String(status) };
    }
  }

  const message = error instanceof Error ? error.message.toLowerCase() : String(error).toLowerCase();

  for (const trigger of FAILOVER_TRIGGER_MESSAGES) {
    if (message.includes(trigger)) {
      return { shouldFailover: true, reason: `network/timeout: ${trigger}`, errorCode: 'NETWORK_ERROR' };
    }
  }

  for (const noFailover of DO_NOT_FAILOVER_MESSAGES) {
    if (message.includes(noFailover)) {
      return { shouldFailover: false, reason: `client error: ${noFailover}`, errorCode: 'CLIENT_ERROR' };
    }
  }

  return { shouldFailover: true, reason: 'unknown error', errorCode: 'UNKNOWN' };
}

function logAttempt(log: AttemptLog): void {
  attemptLogs.push(log);
  if (attemptLogs.length > 1000) {
    attemptLogs.shift();
  }
}

function updateMetrics(success: boolean, latencyMs: number, modelPriority: number, failoverReason?: string): void {
  metrics.totalRequests++;
  if (success) {
    metrics.successfulRequests++;
  } else {
    metrics.failedRequests++;
    if (failoverReason) {
      metrics.failureReasons[failoverReason] = (metrics.failureReasons[failoverReason] ?? 0) + 1;
      if (failoverReason.includes('429') || failoverReason.includes('rate limit')) {
        metrics.rateLimitCount++;
      } else if (failoverReason.includes('timeout') || failoverReason.includes('408') || failoverReason.includes('504')) {
        metrics.timeoutCount++;
      } else if (failoverReason.includes('500') || failoverReason.includes('502') || failoverReason.includes('503')) {
        metrics.providerErrorCount++;
      }
    }
  }

  const totalLatency = metrics.averageLatencyMs * (metrics.totalRequests - 1) + latencyMs;
  metrics.averageLatencyMs = Math.round(totalLatency / metrics.totalRequests);

  if (modelPriority === 1) {
    const total = metrics.primarySuccessRate * 100;
    metrics.primarySuccessRate = Math.round((total + (success ? 100 : 0)) / (metrics.totalRequests * 100) * 100) / 100;
  } else if (modelPriority === 2) {
    const total = metrics.fallbackSuccessRate * 100;
    metrics.fallbackSuccessRate = Math.round((total + (success ? 100 : 0)) / (metrics.totalRequests * 100) * 100) / 100;
  } else if (modelPriority === 3) {
    const total = metrics.secondarySuccessRate * 100;
    metrics.secondarySuccessRate = Math.round((total + (success ? 100 : 0)) / (metrics.totalRequests * 100) * 100) / 100;
  }
}

function createTimeoutController(): AbortController {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  return controller;
}

function createClient(): OpenAI {
  const apiKey = process.env.SENTINELX_API_KEY || process.env.OPENROUTER_API_KEY;
  const baseURL = process.env.SENTINELX_BASE_URL || process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1';

  if (!apiKey) {
    throw new Error('API Key not configured');
  }

  return new OpenAI({
    apiKey,
    baseURL,
    defaultHeaders: {
      'HTTP-Referer': 'https://sentinelx.ai',
      'X-Title': 'SentinelX AI Governance Firewall',
    },
  });
}

async function attemptCompletion(
  client: OpenAI,
  model: string,
  params: CompleteParams,
  attemptNumber: number,
  _modelPriority: number,
): Promise<{ result?: CompleteResult; error?: Error; failover: boolean; reason: string; errorCode?: string }> {
  const startedAt = performance.now();
  const controller = createTimeoutController();

  try {
    const res = await client.chat.completions.create({
      model,
      messages: params.messages as OpenAI.Chat.ChatCompletionMessageParam[],
      temperature: params.temperature ?? 0.3,
      max_tokens: params.maxTokens ?? 1024,
      response_format: params.jsonMode ? { type: 'json_object' } : undefined,
    }, {
      signal: controller.signal,
    });

    const text = res.choices[0]?.message?.content ?? '';
    const usage = res.usage;
    const promptTokens = usage?.prompt_tokens ?? estimateTokens(params.messages);
    const completionTokens = usage?.completion_tokens ?? estimateTokens([{ role: 'assistant', content: text }]);
    const latencyMs = Math.round(performance.now() - startedAt);

    logAttempt({
      attemptNumber,
      model,
      status: 'success',
      latencyMs,
    });

    return {
      result: {
        text,
        model,
        provider: 'openrouter',
        promptTokens,
        completionTokens,
        totalTokens: promptTokens + completionTokens,
        estimatedCostUsd: estimateCost(model, promptTokens, completionTokens),
        latencyMs,
        simulated: false,
        attemptNumber,
        failoverOccurred: attemptNumber > 1,
        failoverReason: attemptNumber > 1 ? `Failover from previous model (attempt ${attemptNumber - 1})` : undefined,
      },
      failover: false,
      reason: 'success',
    };
  } catch (err) {
    const latencyMs = Math.round(performance.now() - startedAt);
    const error = err instanceof Error ? err : new Error(String(err));

    const { shouldFailover, reason, errorCode } = determineFailover(error, attemptNumber);

    logAttempt({
      attemptNumber,
      model,
      status: 'failed',
      latencyMs,
      reason,
      errorCode,
    });

    return {
      error,
      failover: shouldFailover,
      reason,
      errorCode,
    };
  }
}

export async function completeWithFailover(params: CompleteParams): Promise<CompleteResult> {
  const models = getModelConfigs();
  const client = createClient();
  let attemptNumber = 0;
  let lastError: Error | undefined;
  let lastFailoverReason: string | undefined;

  for (const modelConfig of models) {
    for (let retry = 0; retry <= MAX_ATTEMPTS_PER_MODEL; retry++) {
      attemptNumber++;
      const { result, error, failover, reason, errorCode } = await attemptCompletion(
        client,
        modelConfig.name,
        params,
        attemptNumber,
        modelConfig.priority,
      );

      if (result) {
        lastSuccessfulModel = modelConfig.name;
        apiConnectivity = true;
        updateMetrics(true, result.latencyMs, modelConfig.priority);
        return result;
      }

      lastError = error;
      lastFailoverReason = reason;
      updateMetrics(false, 0, modelConfig.priority, reason);

      if (!failover) {
        const finalError = new Error(`OpenRouter failed: ${lastError?.message ?? 'Unknown error'}`);
        (finalError as any).errorCode = errorCode;
        (finalError as any).attempts = attemptNumber;
        (finalError as any).failoverReason = lastFailoverReason;
        throw finalError;
      }
    }
  }

  const finalError = new Error(`All OpenRouter models exhausted after ${attemptNumber} attempts. Last error: ${lastError?.message ?? 'Unknown error'}`);
  (finalError as any).errorCode = 'ALL_MODELS_FAILED';
  (finalError as any).attempts = attemptNumber;
  (finalError as any).failoverReason = lastFailoverReason;
  throw finalError;
}

export async function completeJsonWithFailover<T>(params: CompleteParams): Promise<T> {
  const res = await completeWithFailover({ ...params, jsonMode: true });
  try {
    return JSON.parse(res.text) as T;
  } catch {
    const match = res.text.match(/\{[\s\S]*\}/);
    if (match) return JSON.parse(match[0]) as T;
    throw new Error('OpenRouter returned non-JSON');
  }
}

export function getOpenRouterMetrics(): OpenRouterMetrics {
  return { ...metrics };
}

export function getOpenRouterAttemptLogs(): AttemptLog[] {
  return [...attemptLogs];
}

export function getOpenRouterHealthCheck(): HealthCheckResult {
  const models = getModelConfigs();
  return {
    configuredModels: models.map(m => m.name),
    currentDefault: models[0]?.name ?? 'none',
    apiConnectivity,
    providerStatus: apiConnectivity ? 'healthy' : 'unhealthy',
    lastSuccessfulModel,
    successRates: {
      primary: metrics.primarySuccessRate,
      fallback: metrics.fallbackSuccessRate,
      secondary: metrics.secondarySuccessRate,
    },
    averageLatencyMs: metrics.averageLatencyMs,
  };
}

export function resetOpenRouterMetrics(): void {
  metrics.primarySuccessRate = 0;
  metrics.fallbackSuccessRate = 0;
  metrics.secondarySuccessRate = 0;
  metrics.averageLatencyMs = 0;
  metrics.failureReasons = {};
  metrics.timeoutCount = 0;
  metrics.rateLimitCount = 0;
  metrics.providerErrorCount = 0;
  metrics.totalRequests = 0;
  metrics.successfulRequests = 0;
  metrics.failedRequests = 0;
  attemptLogs.length = 0;
  lastSuccessfulModel = null;
  apiConnectivity = false;
}