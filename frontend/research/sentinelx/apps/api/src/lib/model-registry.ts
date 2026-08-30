export interface ModelMetadata {
  id: string;
  provider: string;
  displayName: string;
  inputCostPerMillion: number;
  outputCostPerMillion: number;
  capabilities: {
    coding: boolean;
    reasoning: boolean;
    vision: boolean;
  };
  contextWindow: number;
  enabled: boolean;
  priority: number;
}

export const MODEL_REGISTRY: Record<string, ModelMetadata> = {
  'openai/gpt-4o-mini': {
    id: 'openai/gpt-4o-mini',
    provider: 'openai',
    displayName: 'GPT-4o Mini',
    inputCostPerMillion: 0.15,
    outputCostPerMillion: 0.60,
    capabilities: { coding: true, reasoning: true, vision: true },
    contextWindow: 128000,
    enabled: true,
    priority: 10,
  },
  'openai/gpt-4o': {
    id: 'openai/gpt-4o',
    provider: 'openai',
    displayName: 'GPT-4o',
    inputCostPerMillion: 5.0,
    outputCostPerMillion: 15.0,
    capabilities: { coding: true, reasoning: true, vision: true },
    contextWindow: 128000,
    enabled: true,
    priority: 5,
  },
  'claude/claude-3-5-sonnet': {
    id: 'claude/claude-3-5-sonnet',
    provider: 'claude',
    displayName: 'Claude 3.5 Sonnet',
    inputCostPerMillion: 3.0,
    outputCostPerMillion: 15.0,
    capabilities: { coding: true, reasoning: true, vision: true },
    contextWindow: 200000,
    enabled: true,
    priority: 10,
  },
  'gemini/gemini-1.5-flash': {
    id: 'gemini/gemini-1.5-flash',
    provider: 'gemini',
    displayName: 'Gemini 1.5 Flash',
    inputCostPerMillion: 0.075,
    outputCostPerMillion: 0.30,
    capabilities: { coding: true, reasoning: true, vision: true },
    contextWindow: 1000000,
    enabled: true,
    priority: 10,
  },
  'gemini/gemini-1.5-pro': {
    id: 'gemini/gemini-1.5-pro',
    provider: 'gemini',
    displayName: 'Gemini 1.5 Pro',
    inputCostPerMillion: 3.50,
    outputCostPerMillion: 10.50,
    capabilities: { coding: true, reasoning: true, vision: true },
    contextWindow: 2000000,
    enabled: true,
    priority: 5,
  },
};

export function getModelMetadata(modelId: string): ModelMetadata | null {
  return MODEL_REGISTRY[modelId] || null;
}

export function calculateEstimatedCost(modelId: string, inputTokens: number, outputTokens: number): number {
  const meta = getModelMetadata(modelId);
  if (!meta) return 0;
  
  const inputCost = (inputTokens / 1_000_000) * meta.inputCostPerMillion;
  const outputCost = (outputTokens / 1_000_000) * meta.outputCostPerMillion;
  return inputCost + outputCost;
}
