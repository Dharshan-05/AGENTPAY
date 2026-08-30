import type { InspectorOutput, SeverityLevel } from '../lib/types';

import { Severity } from '../lib/types';

import { BaseAgent } from './base';

const TOPIC_KEYWORDS: Array<[RegExp, string, number]> = [
  [/\b(salary|ctc|compensation|payroll|payslip)\b/i, 'HR / Compensation', 9],
  [/\b(patient|diagnos|medical|health|prescription)\b/i, 'Healthcare', 9],
  [/\b(card|payment|bank|account|invoice|transaction|balance)\b/i, 'Finance', 8],
  [/\b(contract|nda|legal|lawsuit|client|proposal)\b/i, 'Legal', 7],
  [/\b(deploy|production|server|database|kubernetes|docker|aws|azure|gcp)\b/i, 'Infrastructure', 6],
  [/\b(code|function|api|bug|refactor|debug|python|javascript)\b/i, 'Software Engineering', 3],
  [/\b(customer|user data|lead|pii|personal)\b/i, 'Customer Data', 7],
  [/\b(strategy|roadmap|product|revenue|forecast|q[1-4])\b/i, 'Business Strategy', 5],
  [/\b(research|paper|analysis|report|summary)\b/i, 'Research & Analysis', 2],
];

const SENSITIVE_ACTIONS = [
  /\b(summar|analyse|analyze|review)\b/i,
  /\b(extract|parse|scrape|pull|retrieve)\b/i,
  /\b(compare|aggregate|consolidate)\b/i,
];

export class InspectorAgent extends BaseAgent<string, InspectorOutput> {
  constructor() {
    super(
      'inspector-agent',
      'Analyse the incoming prompt: classify intent, topic, and data sensitivity before any processing begins.',
      '1.2.0',
    );
  }

  protected async execute(prompt: string): Promise<InspectorOutput> {
    const wordCount = prompt.split(/\s+/).filter(Boolean).length;
    const intent = this.detectIntent(prompt);
    const [topicCategory, dataSensitivity] = this.classifyTopic(prompt);
    const containsSensitiveData = this.hasSensitiveMarkers(prompt);

    return {
      language: 'en',
      intent,
      topicCategory,
      dataSensitivity,
      containsSensitiveData,
      wordCount,
    };
  }

  protected calculateConfidence(output: InspectorOutput): number {
    const base = 0.9 - (output.wordCount > 300 ? 0.15 : 0);
    return Math.max(0.6, base);
  }

  private detectIntent(prompt: string): string {
    for (const re of SENSITIVE_ACTIONS) {
      if (re.test(prompt)) {
        return `Analysis / ${re.source.replace(/\\/g, '').replace(/[.*+?^${}()|[\]\\]/g, '')}`;
      }
    }
    return 'General query';
  }

  private classifyTopic(prompt: string): [string, number] {
    let bestTopic = 'General';
    let bestScore = 0;
    for (const entry of TOPIC_KEYWORDS) {
      const re = entry[0];
      const topic = entry[1];
      const score = entry[2];
      if (re.test(prompt) && score > bestScore) {
        bestTopic = topic;
        bestScore = score;
      }
    }
    return [bestTopic, bestScore];
  }

  private hasSensitiveMarkers(prompt: string): boolean {
    return TOPIC_KEYWORDS.some(([re, , score]) => score >= 7 && re.test(prompt));
  }
}

export function worstSeverityOfSecrets(secrets: Array<{ severity: SeverityLevel }>): SeverityLevel {
  const order: SeverityLevel[] = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO];
  for (const level of order) {
    if (secrets.some((s) => s.severity === level)) return level;
  }
  return Severity.INFO;
}
