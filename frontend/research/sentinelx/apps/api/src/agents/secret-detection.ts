import type { DetectedSecret } from '../lib/types';

import { detectSecrets } from '../engines/detectors';
import { BaseAgent } from './base';

export class SecretDetectionAgent extends BaseAgent<string, DetectedSecret[]> {
  constructor() {
    super(
      'secret-detection-agent',
      'Scan prompt content with 30+ deterministic pattern rules to detect secrets, credentials, and sensitive data.',
      '2.1.0',
    );
  }

  protected async execute(prompt: string): Promise<DetectedSecret[]> {
    return detectSecrets(prompt);
  }

  protected calculateConfidence(output: DetectedSecret[]): number {
    if (output.length === 0) return 0.98;
    const avg = output.reduce((acc, s) => acc + s.confidence, 0) / output.length;
    return Math.max(avg, 0.6);
  }
}
