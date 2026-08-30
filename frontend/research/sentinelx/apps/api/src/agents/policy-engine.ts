import type { DetectedSecret, PolicyViolation } from '../lib/types';

import { evaluatePolicies } from '../engines/policies';
import { BaseAgent } from './base';

export class PolicyEngineAgent extends BaseAgent<DetectedSecret[], PolicyViolation[]> {
  constructor() {
    super(
      'policy-engine',
      'Evaluate detected secrets against GDPR, HIPAA, PCI DSS, SOC 2, ISO 27001, and corporate policy packs.',
      '1.4.0',
    );
  }

  protected async execute(secrets: DetectedSecret[]): Promise<PolicyViolation[]> {
    return evaluatePolicies(secrets);
  }

  protected calculateConfidence(output: PolicyViolation[]): number {
    if (output.length === 0) return 0.97;
    return Math.min(0.99, 0.85 + output.length * 0.02);
  }
}
