import { BaseAgent } from './base';
import { complete, isProviderConfigured } from '../llm/providers';
import { pickProvider } from '../llm/ai';
import type { RiskAssessment } from '../lib/types';

export interface AdaptiveRiskInput {
  prompt: string;
  risk: RiskAssessment;
  department?: string;
}

export interface AdaptiveRiskOutput {
  adjustedScore: number;
  delta: number;
  aiReasoning: string;
  simulated: boolean;
}

export const ADAPTIVE_RISK_ENABLED = process.env.ADAPTIVE_RISK_AI === '1';

export class AdaptiveRiskAgent extends BaseAgent<AdaptiveRiskInput, AdaptiveRiskOutput> {
  constructor() {
    super(
      'adaptive-risk',
      'Blend deterministic rule scoring with an AI contextual assessment to produce an adaptive composite risk score.',
      '1.0.0',
    );
  }

  protected async execute(input: AdaptiveRiskInput): Promise<AdaptiveRiskOutput> {
    const provider = pickProvider();
    if (!ADAPTIVE_RISK_ENABLED || !isProviderConfigured(provider)) {
      return {
        adjustedScore: input.risk.score,
        delta: 0,
        aiReasoning: 'Adaptive risk disabled or no LLM provider configured; rule-based score used.',
        simulated: true,
      };
    }

    try {
      const messages = [
        {
          role: 'system' as const,
          content:
            'You are the SentinelX adaptive risk analyst. Given a prompt, the deterministic rule-based risk score (0-100), and the department, assess whether the context raises or lowers the risk. Reply with a JSON object: { delta: number, reasoning: string }. delta is between -10 and +12 (positive = riskier). Base your judgment on contextual clues the rule engine may miss (e.g. exfiltration phrasing, insider tone, sensitive topic). Be conservative: only deviate when there is a clear contextual signal. Reply with ONLY the JSON.',
        },
        {
          role: 'user' as const,
          content: JSON.stringify({
            prompt: input.prompt.slice(0, 300),
            ruleScore: input.risk.score,
            threatLevel: input.risk.threatLevel,
            department: input.department ?? null,
          }),
        },
      ];
      const res = await complete({ provider, model: 'auto', messages, temperature: 0.2, maxTokens: 160, jsonMode: true });
      if (res.simulated) return this.simulated(input);
      let delta = 0;
      let reasoning = '';
      try {
        const parsed = JSON.parse(res.text);
        delta = Math.max(-10, Math.min(12, Number(parsed.delta) || 0));
        reasoning = String(parsed.reasoning || '').slice(0, 220);
      } catch {
        const match = res.text.match(/\{[\s\S]*\}/);
        if (match) {
          const parsed = JSON.parse(match[0]);
          delta = Math.max(-10, Math.min(12, Number(parsed.delta) || 0));
          reasoning = String(parsed.reasoning || '').slice(0, 220);
        }
      }
      const adjusted = Math.max(0, Math.min(100, input.risk.score + delta));
      return { adjustedScore: adjusted, delta, aiReasoning: reasoning || 'No clear contextual signal detected.', simulated: false };
    } catch {
      return this.simulated(input);
    }
  }

  private simulated(input: AdaptiveRiskInput): AdaptiveRiskOutput {
    return {
      adjustedScore: input.risk.score,
      delta: 0,
      aiReasoning: 'AI assessment unavailable; rule-based composite score applied.',
      simulated: true,
    };
  }

  protected calculateConfidence(output: AdaptiveRiskOutput): number {
    return output.simulated ? 0.5 : 0.9;
  }
}
