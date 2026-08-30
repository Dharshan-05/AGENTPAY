import { BaseAgent } from './base';
import { rewritePromptAI } from '../llm/ai';
import { rewritePrompt } from '../engines/rewriter';
import type { DetectedSecret, RiskAssessment } from '../lib/types';

export interface RewriterInput {
  prompt: string;
  secrets: DetectedSecret[];
  risk: RiskAssessment;
}

export interface RewriterOutput {
  rewritten: string;
  redactions: Array<{ original: string; replacement: string }>;
  changed: boolean;
}

export const AI_REWRITE_ENABLED = process.env.AI_REWRITE === '1';

export class RewriterAgent extends BaseAgent<RewriterInput, RewriterOutput> {
  constructor() {
    super(
      'prompt-rewriter',
      'Sanitise the prompt by removing sensitive entities while preserving the user\'s original intent.',
      '1.2.0',
    );
  }

  protected async execute(input: RewriterInput): Promise<RewriterOutput> {
    if (input.secrets.length === 0 && input.risk.score < 35) {
      return { rewritten: input.prompt, redactions: [], changed: false };
    }

    if (AI_REWRITE_ENABLED) {
      try {
        const ai = await rewritePromptAI({
          original: input.prompt,
          secrets: input.secrets.map((s) => ({ label: s.label, value: s.match })),
        });
        if (!ai.simulated && ai.result && ai.result !== input.prompt) {
          return {
            rewritten: ai.result,
            redactions: input.secrets.map((s) => ({ original: s.match, replacement: `[REDACTED ${s.label.toUpperCase()}]` })),
            changed: true,
          };
        }
      } catch {
        // fall through to deterministic engine
      }
    }

    const { rewritten, redactions } = rewritePrompt(input.prompt, input.secrets);
    return { rewritten, redactions, changed: rewritten !== input.prompt };
  }

  protected calculateConfidence(output: RewriterOutput): number {
    if (!output.changed) return 0.95;
    return Math.max(0.7, 1 - output.redactions.length * 0.03);
  }
}
