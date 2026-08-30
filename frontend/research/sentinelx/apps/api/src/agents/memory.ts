import { BaseAgent } from './base';

export interface MemoryInput {
  userId?: string;
  sessionId?: string;
  prompt: string;
  riskScore: number;
}

export interface MemoryOutput {
  userId?: string;
  sessionId?: string;
  contextStored: boolean;
  recentActivity: number;
}

export class MemoryAgent extends BaseAgent<MemoryInput, MemoryOutput> {
  constructor() {
    super(
      'memory-agent',
      'Store session context and user behavioural signals for historical risk analysis and copilot recall.',
      '1.0.0',
    );
  }

  protected async execute(input: MemoryInput): Promise<MemoryOutput> {
    const recentActivity = input.sessionId
      ? (await import('../lib/redis')).cacheIncr(`session:${input.sessionId}:events`, 3600)
      : Promise.resolve(0);

    return {
      userId: input.userId,
      sessionId: input.sessionId,
      contextStored: true,
      recentActivity: await recentActivity,
    };
  }

  protected calculateConfidence(): number {
    return 0.95;
  }
}
