import type { DetectedSecret, InspectorOutput, PolicyViolation, RiskAssessment } from '../lib/types';

import { assessRisk } from '../engines/risk';
import { store } from '../lib/store';
import { BaseAgent } from './base';

export interface RiskEngineInput {
  secrets: DetectedSecret[];
  violations: PolicyViolation[];
  inspector: InspectorOutput;
  userId?: string;
}

export class RiskEngineAgent extends BaseAgent<RiskEngineInput, RiskAssessment> {
  constructor() {
    super(
      'risk-engine',
      'Compute a live enterprise risk score from severity, confidence, data sensitivity, prompt intent, policy violations, and historical behaviour.',
      '1.3.0',
    );
  }

  protected async execute(input: RiskEngineInput): Promise<RiskAssessment> {
    const historical = await this.historicalRisk(input.userId);
    return assessRisk({
      secrets: input.secrets,
      violations: input.violations,
      inspector: input.inspector,
      historicalRisk: historical.average,
      historyCount: historical.count,
    });
  }

  protected calculateConfidence(output: RiskAssessment): number {
    return output.confidence;
  }

  private async historicalRisk(userId?: string): Promise<{ average: number; count: number }> {
    if (!userId) return { average: 0, count: 0 };
    try {
      const events = await store.auditLog.findMany({
        where: { userId },
        orderBy: { timestamp: 'desc' },
        take: 20,
      });
      const risky = (events as Array<{ riskScore: number }>).filter((e) => e.riskScore > 0);
      if (risky.length === 0) return { average: 0, count: 0 };
      const average = risky.reduce((acc, e) => acc + e.riskScore, 0) / risky.length;
      return { average, count: risky.length };
    } catch {
      return { average: 0, count: 0 };
    }
  }
}
