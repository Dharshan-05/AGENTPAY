import 'dotenv/config';
import OpenAI from 'openai';
import Anthropic from '@anthropic-ai/sdk';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { estimateTokens, estimateCost } from './tokens';
import type { OpenRouterMetrics, HealthCheckResult } from './openrouter';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface CompleteParams {
  provider: string;
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  maxTokens?: number;
  jsonMode?: boolean;
}

export interface CompleteResult {
  text: string;
  provider: string;
  model: string;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  estimatedCostUsd: number;
  latencyMs: number;
  simulated: boolean;
  attemptNumber?: number;
  failoverOccurred?: boolean;
  failoverReason?: string;
}

export interface ProviderStatus {
  id: string;
  configured: boolean;
  defaultModel: string;
  model?: string;
}

const OLLAMA_BASE = process.env.OLLAMA_BASE_URL ?? 'http://localhost:11434';

export const PROVIDER_MODELS: Record<string, string> = {
  openai: process.env.DEFAULT_LLM_MODEL_OPENAI ?? 'gpt-4o-mini',
  openrouter: process.env.DEFAULT_LLM_MODEL_OPENROUTER ?? 'openai/gpt-4o-mini',
  gemini: process.env.DEFAULT_LLM_MODEL_GEMINI ?? 'gemini-1.5-flash',
  claude: process.env.DEFAULT_LLM_MODEL_CLAUDE ?? 'claude-3-5-haiku-20241022',
  ollama: process.env.DEFAULT_LLM_MODEL_OLLAMA ?? 'llama3.1',
};

const ENV_KEYS: Record<string, string> = {
  openai: 'OPENAI_API_KEY',
  openrouter: 'OPENROUTER_API_KEY',
  gemini: 'GEMINI_API_KEY',
  claude: 'ANTHROPIC_API_KEY',
  ollama: 'OLLAMA_API_KEY',
};

export function isProviderConfigured(provider: string): boolean {
  if (provider === 'ollama') return process.env.OLLAMA_ENABLED === '1';
  const key = ENV_KEYS[provider];
  return Boolean(key && process.env[key]);
}

export function listProviderStatus(): ProviderStatus[] {
  return Object.keys(PROVIDER_MODELS).map((id) => ({
    id,
    configured: isProviderConfigured(id),
    defaultModel: PROVIDER_MODELS[id],
  }));
}

export function resolveModel(provider: string, requested: string): string {
  if (requested && requested !== 'auto') return requested;
  return PROVIDER_MODELS[provider] ?? 'gpt-4o-mini';
}

export async function getOpenRouterMetricsExport(): Promise<OpenRouterMetrics> {
  const { getOpenRouterMetrics } = await import('./openrouter');
  return getOpenRouterMetrics();
}

export async function getOpenRouterHealthCheckExport(): Promise<HealthCheckResult> {
  const { getOpenRouterHealthCheck } = await import('./openrouter');
  return getOpenRouterHealthCheck();
}

export async function resetOpenRouterMetricsExport(): Promise<void> {
  const { resetOpenRouterMetrics } = await import('./openrouter');
  resetOpenRouterMetrics();
}

function simulateCompletion(params: CompleteParams): CompleteResult {
  const model = resolveModel(params.provider, params.model);
  const text = `[simulated ${params.provider}/${model}] ${params.messages.at(-1)?.content.slice(0, 300)}...`;
  const promptTokens = estimateTokens(params.messages);
  const completionTokens = estimateTokens([{ role: 'assistant', content: text }]);
  return {
    text,
    provider: params.provider,
    model,
    promptTokens,
    completionTokens,
    totalTokens: promptTokens + completionTokens,
    estimatedCostUsd: estimateCost(model, promptTokens, completionTokens),
    latencyMs: 0,
    simulated: true,
  };
}

export let completeMock: ((params: CompleteParams) => Promise<CompleteResult>) | null = null;
export function setCompleteMock(mock: typeof completeMock) { completeMock = mock; }

export async function complete(params: CompleteParams): Promise<CompleteResult> {
  if (completeMock) return completeMock(params);
  const startedAt = performance.now();
  const provider = params.provider;
  const model = resolveModel(provider, params.model);
  const key = ENV_KEYS[provider];
  const apiKey = process.env[key];

  const sentinelxKey = process.env.SENTINELX_API_KEY;

  if (!apiKey && !sentinelxKey && provider !== 'ollama') {
    return simulateCompletion(params);
  }

  try {

    let text = '';
    switch (provider) {
      case 'openai':
      case 'openrouter': {
        const client = new OpenAI({
          apiKey: process.env.SENTINELX_API_KEY || apiKey || 'sk-local',
          baseURL: process.env.SENTINELX_BASE_URL,
        });
        const res = await client.chat.completions.create({
          model: params.model ?? 'gpt-4o-mini', // use requested model or default
          messages: params.messages as OpenAI.Chat.ChatCompletionMessageParam[],
          temperature: params.temperature ?? 0.3,
          max_tokens: params.maxTokens ?? 1024,
          response_format: params.jsonMode ? { type: 'json_object' } : undefined,
        });
        text = res.choices[0]?.message?.content ?? '';
        const usage = res.usage;
        const promptTokens = usage?.prompt_tokens ?? estimateTokens(params.messages);
        const completionTokens = usage?.completion_tokens ?? estimateTokens([{ role: 'assistant', content: text }]);
        return {
          text,
          provider,
          model,
          promptTokens,
          completionTokens,
          totalTokens: promptTokens + completionTokens,
          estimatedCostUsd: estimateCost(model, promptTokens, completionTokens),
          latencyMs: Math.round(performance.now() - startedAt),
          simulated: false,
        };
      }
      case 'claude': {
        const client = new Anthropic({ apiKey: apiKey });
        const res = await client.messages.create({
          model,
          max_tokens: params.maxTokens ?? 1024,
          temperature: params.temperature ?? 0.3,
          system: params.messages.find((m) => m.role === 'system')?.content ?? undefined,
          messages: params.messages
            .filter((m) => m.role !== 'system')
            .map((m) => ({ role: m.role as 'user' | 'assistant', content: m.content })),
        });
        text = res.content
          .filter((b) => b.type === 'text')
          .map((b) => (b as { text: string }).text)
          .join('');
        const promptTokens = res.usage.input_tokens;
        const completionTokens = res.usage.output_tokens;
        return {
          text,
          provider,
          model,
          promptTokens,
          completionTokens,
          totalTokens: promptTokens + completionTokens,
          estimatedCostUsd: estimateCost(model, promptTokens, completionTokens),
          latencyMs: Math.round(performance.now() - startedAt),
          simulated: false,
        };
      }
      case 'gemini': {
        const genai = new GoogleGenerativeAI(apiKey ?? '');
        const gemModel = genai.getGenerativeModel({ model });
        const system = params.messages.find((m) => m.role === 'system')?.content;
        const res = await gemModel.generateContent({
          contents: params.messages
            .filter((m) => m.role !== 'system')
            .map((m) => ({
              role: m.role === 'assistant' ? ('model' as const) : ('user' as const),
              parts: [{ text: m.content }],
            })),
          systemInstruction: system ? { role: 'user', parts: [{ text: system }] } : undefined,
        });
        text = res.response.text();
        const promptTokens = estimateTokens(params.messages);
        const completionTokens = estimateTokens([{ role: 'assistant', content: text }]);
        return {
          text,
          provider,
          model,
          promptTokens,
          completionTokens,
          totalTokens: promptTokens + completionTokens,
          estimatedCostUsd: estimateCost(model, promptTokens, completionTokens),
          latencyMs: Math.round(performance.now() - startedAt),
          simulated: false,
        };
      }
      case 'ollama': {
        const res = await fetch(`${OLLAMA_BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model, messages: params.messages, stream: false }),
        });
        if (!res.ok) throw new Error(`ollama returned ${res.status}`);
        const data: any = await res.json();
        text = data.message?.content ?? '';
        const promptTokens = data.prompt_eval_count ?? estimateTokens(params.messages);
        const completionTokens = data.eval_count ?? estimateTokens([{ role: 'assistant', content: text }]);
        return {
          text,
          provider,
          model,
          promptTokens,
          completionTokens,
          totalTokens: promptTokens + completionTokens,
          estimatedCostUsd: 0,
          latencyMs: Math.round(performance.now() - startedAt),
          simulated: false,
        };
      }
      default:
        return simulateCompletion(params);
    }
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    if (process.env.LLM_SILENT === '1') {
      return simulateCompletion(params);
    }
    throw new Error(`LLM ${provider} failed: ${msg}`);
  }
}

export async function completeJson<T>(params: CompleteParams): Promise<T> {
  if (params.provider === 'openrouter') {
    const { completeJsonWithFailover } = await import('./openrouter');
    return completeJsonWithFailover<T>({
      messages: params.messages,
      temperature: params.temperature,
      maxTokens: params.maxTokens,
    });
  }

  const res = await complete({ ...params, jsonMode: true });
  if (res.simulated) {
    throw new Error('simulated');
  }
  try {
    return JSON.parse(res.text) as T;
  } catch {
    const match = res.text.match(/\{[\s\S]*\}/);
    if (match) return JSON.parse(match[0]) as T;
    throw new Error('LLM returned non-JSON');
  }
}
