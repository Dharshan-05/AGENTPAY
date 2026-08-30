import { getModelMetadata } from './model-registry';
import { store } from './store';
import { complete } from '../llm/providers';
import type { ChatMessage, CompleteResult } from '../llm/providers';

export interface RouteDecision {
  allowed: boolean;
  modelQueue: string[];
  routingReason: string;
  errorMessage?: string;
  errorCode?: string;
}

export async function resolveAndRouteModel(
  requestedModel: string,
  userId: string,
  organizationId: string | null,
  messages: ChatMessage[]
): Promise<RouteDecision> {
  // Load permissions
  const modelPerm = await store.employeeModelPermission.findFirst({
    where: { userId },
  }).catch(() => null);

  const provPerm = await store.employeeProviderPermission.findFirst({
    where: { userId },
  }).catch(() => null);

  let allowedModels = modelPerm?.allowedModels ? (modelPerm.allowedModels as string[]) : [];
  let deniedModels = modelPerm?.deniedModels ? (modelPerm.deniedModels as string[]) : [];
  
  let allowedProviders = provPerm?.allowedProviders ? (provPerm.allowedProviders as string[]) : [];
  let deniedProviders = provPerm?.deniedProviders ? (provPerm.deniedProviders as string[]) : [];

  // Fallback to org permissions if user permissions are empty (simple inheritance)
  if (organizationId) {
    if (!allowedModels.length && !deniedModels.length) {
      const orgModel = await store.employeeModelPermission.findFirst({ where: { organizationId, userId: null } }).catch(() => null);
      if (orgModel) {
        allowedModels = orgModel.allowedModels as string[];
        deniedModels = orgModel.deniedModels as string[];
      }
    }
    if (!allowedProviders.length && !deniedProviders.length) {
      const orgProv = await store.employeeProviderPermission.findFirst({ where: { organizationId, userId: null } }).catch(() => null);
      if (orgProv) {
        allowedProviders = orgProv.allowedProviders as string[];
        deniedProviders = orgProv.deniedProviders as string[];
      }
    }
  }

  const isModelAllowed = (modelId: string) => {
    if (deniedModels.includes(modelId)) return false;
    if (allowedModels.length > 0 && !allowedModels.includes(modelId)) return false;
    
    const meta = getModelMetadata(modelId);
    if (!meta || !meta.enabled) return false;

    if (deniedProviders.includes(meta.provider)) return false;
    if (allowedProviders.length > 0 && !allowedProviders.includes(meta.provider)) return false;

    return true;
  };

  if (requestedModel !== 'sentinel-auto' && requestedModel !== 'auto') {
    // Exact match aliases
    const aliases: Record<string, string> = {
      'gpt-4o': 'openai/gpt-4o',
      'gpt-4o-mini': 'openai/gpt-4o-mini',
      'claude-3-5-haiku': 'claude/claude-3-5-haiku-20241022',
      'gemini-flash': 'gemini/gemini-1.5-flash',
    };
    const resolvedId = aliases[requestedModel] ?? requestedModel;

    if (!isModelAllowed(resolvedId)) {
      return {
        allowed: false,
        modelQueue: [],
        routingReason: 'explicit model rejected',
        errorCode: 'MODEL_NOT_ALLOWED',
        errorMessage: 'This model is not allowed for your account.',
      };
    }

    // Attempt this model, optionally adding generic fallback if allowed
    const queue = [resolvedId];
    if (isModelAllowed('openai/gpt-4o-mini') && resolvedId !== 'openai/gpt-4o-mini') queue.push('openai/gpt-4o-mini');

    return {
      allowed: true,
      modelQueue: queue,
      routingReason: 'explicit model',
    };
  }

  // Auto routing logic based on prompt features
  let isCoding = false;
  let isReasoning = false;
  let tokenLength = 0;
  
  for (const msg of messages) {
    const text = msg.content.toLowerCase();
    tokenLength += text.length / 4; // rough char to token
    if (text.includes('code') || text.includes('function') || text.includes('script') || text.includes('implement')) {
      isCoding = true;
    }
    if (text.includes('think') || text.includes('analyze') || text.includes('reason') || text.includes('evaluate')) {
      isReasoning = true;
    }
  }

  let preferredModel = '';
  let routingReason = '';

  if (tokenLength > 100000) {
    preferredModel = 'gemini/gemini-1.5-pro';
    routingReason = 'large context capability';
  } else if (isReasoning) {
    preferredModel = 'openai/gpt-4o';
    routingReason = 'reasoning capability';
  } else if (isCoding) {
    preferredModel = 'claude/claude-3-5-sonnet';
    routingReason = 'coding capability';
  } else {
    preferredModel = 'openai/gpt-4o-mini';
    routingReason = 'low_cost_default';
  }

  const modelQueue: string[] = [];
  
  // Try preferred model
  if (isModelAllowed(preferredModel)) {
    modelQueue.push(preferredModel);
  }
  
  // Fallbacks
  const fallbacks = ['openai/gpt-4o-mini', 'gemini/gemini-1.5-flash'];
  for (const f of fallbacks) {
    if (f !== preferredModel && isModelAllowed(f)) {
      modelQueue.push(f);
    }
  }

  if (modelQueue.length === 0) {
    return {
      allowed: false,
      modelQueue: [],
      routingReason: 'no available allowed models',
      errorCode: 'MODEL_NOT_ALLOWED',
      errorMessage: 'No authorized models available to handle the request.',
    };
  }

  return {
    allowed: true,
    modelQueue,
    routingReason,
  };
}

export interface FailoverResult extends CompleteResult {
  attemptCount: number;
  routingReason: string;
}

export async function executeWithFailover(
  queue: string[],
  routingReason: string,
  params: { messages: ChatMessage[]; temperature?: number; maxTokens?: number; }
): Promise<FailoverResult> {
  let lastError: Error | null = null;
  let attemptCount = 0;

  for (const modelId of queue) {
    attemptCount++;
    const meta = getModelMetadata(modelId);
    const rawProvider = meta ? meta.provider : modelId.split('/')[0] || 'unknown';
    const rawModel = meta ? modelId.replace(`${meta.provider}/`, '') : modelId;
    
    try {
      // Create timeout promise
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout
      
      const pResult = complete({
        provider: rawProvider,
        model: rawModel,
        messages: params.messages,
        temperature: params.temperature,
        maxTokens: params.maxTokens,
      });
      
      const res = await Promise.race([
        pResult,
        new Promise<never>((_, reject) => {
          controller.signal.addEventListener('abort', () => reject(new Error('PROVIDER_TIMEOUT')));
        })
      ]);
      clearTimeout(timeoutId);

      return {
        ...res,
        model: modelId,
        provider: rawProvider,
        attemptCount,
        routingReason,
        failoverOccurred: attemptCount > 1,
      };
    } catch (err: any) {
      lastError = err;
      const msg = err.message || '';
      // Do not retry on auth/policy errors
      if (msg.includes('401') || msg.includes('403') || msg.includes('POLICY_BLOCKED')) {
        throw err;
      }
      // Continue to fallback on 429, 5xx, or timeouts
    }
  }

  throw new Error(`ALL_PROVIDERS_FAILED: Last error was ${lastError?.message || 'unknown'}`);
}
