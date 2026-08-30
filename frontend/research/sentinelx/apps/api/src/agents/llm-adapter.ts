import { BaseAgent } from './base';
import { complete } from '../llm/providers';

export interface LLMAdapterInput {
  prompt: string;
  provider: string;
  model: string;
}

export interface LLMAdapterOutput {
  response: string;
  provider: string;
  model: string;
  tokensUsed: number;
  estimatedCostUsd: number;
  latencyMs: number;
  simulated: boolean;
}

export const AVAILABLE_PROVIDERS = ['openai', 'gemini', 'claude', 'ollama', 'openrouter'];

export class LLMAdapterAgent extends BaseAgent<LLMAdapterInput, LLMAdapterOutput> {
  constructor() {
    super(
      'llm-adapter',
      'Route the sanitised prompt to the selected provider (OpenAI, Gemini, Claude, Ollama, OpenRouter) through the SentinelX gateway.',
      '4.0.0',
    );
  }

  protected async execute(input: LLMAdapterInput): Promise<LLMAdapterOutput> {
    const res = await complete({
      provider: input.provider,
      model: input.model,
      messages: [{ role: 'user', content: input.prompt }],
      maxTokens: 512,
      temperature: 0.4,
    });
    return {
      response: res.text,
      provider: res.provider,
      model: res.model,
      tokensUsed: res.totalTokens,
      estimatedCostUsd: res.estimatedCostUsd,
      latencyMs: res.latencyMs,
      simulated: res.simulated,
    };
  }

  protected calculateConfidence(output: LLMAdapterOutput): number {
    return output.simulated ? 0.6 : 0.98;
  }
}
