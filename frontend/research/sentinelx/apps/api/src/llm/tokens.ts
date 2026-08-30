import { encoding_for_model, type TiktokenModel } from 'tiktoken';

const GPT_4O: TiktokenModel = 'gpt-4o';

export function estimateTokens(messages: { role: string; content: string }[]): number {
  try {
    const enc = encoding_for_model(GPT_4O);
    let count = 0;
    for (const m of messages) {
      count += enc.encode(m.content).length + 4;
    }
    enc.free();
    return count;
  } catch {
    return messages.reduce((n, m) => n + Math.ceil(m.content.length / 4), 0);
  }
}

export function estimateTextTokens(text: string): number {
  try {
    const enc = encoding_for_model(GPT_4O);
    const n = enc.encode(text).length;
    enc.free();
    return n;
  } catch {
    return Math.ceil(text.length / 4);
  }
}

export interface PriceTier {
  inputPerM: number;
  outputPerM: number;
}

const PRICING: Record<string, PriceTier> = {
  'gpt-4o-mini': { inputPerM: 0.15, outputPerM: 0.6 },
  'gpt-4o': { inputPerM: 2.5, outputPerM: 10 },
  'openai/gpt-4o-mini': { inputPerM: 0.15, outputPerM: 0.6 },
  'claude-3-5-haiku-20241022': { inputPerM: 0.8, outputPerM: 4 },
  'claude-3-5-sonnet-20241022': { inputPerM: 3, outputPerM: 15 },
  'gemini-1.5-flash': { inputPerM: 0.075, outputPerM: 0.3 },
  'gemini-1.5-pro': { inputPerM: 1.25, outputPerM: 5 },
  'llama3.1': { inputPerM: 0, outputPerM: 0 },
  'llama3.2': { inputPerM: 0, outputPerM: 0 },
};

export function estimateCost(
  model: string,
  promptTokens: number,
  completionTokens: number,
): number {
  const tier = PRICING[model];
  if (!tier) return 0;
  return (promptTokens / 1_000_000) * tier.inputPerM + (completionTokens / 1_000_000) * tier.outputPerM;
}
