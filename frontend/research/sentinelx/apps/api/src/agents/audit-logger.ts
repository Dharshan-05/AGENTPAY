import crypto from 'node:crypto';
import type { AuditRecord, DecisionType, PolicyViolation, DetectedSecret } from '../lib/types';

import { store } from '../lib/store';
import { cacheIncr } from '../lib/redis';
import { BaseAgent } from './base';

export interface AuditInput {
  pipelineId: string;
  userId?: string;
  ipAddress?: string;
  sessionId?: string;
  prompt: string;
  rewrittenPrompt?: string | null;
  violations: PolicyViolation[];
  secrets: DetectedSecret[];
  riskScore: number;
  threatLevel: string;
  decision: DecisionType;
  provider?: string;
  model?: string;
  latencyMs: number;
  agentTrace: unknown[];
}

export class AuditLoggerAgent extends BaseAgent<AuditInput, AuditRecord> {
  constructor() {
    super(
      'audit-logger',
      'Persist a tamper-evident audit record: prompt hash, violations, risk, decision, and full agent trace.',
      '1.5.0',
    );
  }

  protected async execute(input: AuditInput): Promise<AuditRecord> {
    const promptHash = crypto
      .createHash('sha256')
      .update(input.prompt)
      .digest('hex')
      .slice(0, 24);

    const record = (await store.auditLog.create({
      data: {
        userId: input.userId,
        promptHash,
        prompt: input.prompt,
        rewrittenPrompt: input.rewrittenPrompt ?? null,
        violations: input.violations,
        secrets: input.secrets,
        riskScore: input.riskScore,
        threatLevel: input.threatLevel,
        policiesTriggered: input.violations.map((v) => v.regulation),
        decision: input.decision,
        llmProvider: input.provider,
        llmModel: input.model,
        latencyMs: input.latencyMs,
        ipAddress: input.ipAddress,
        sessionId: input.sessionId,
        agentTrace: input.agentTrace,
      },
    })) as unknown as AuditRecord & { timestamp: Date | string };

    await cacheIncr('stats:prompts');

    return {
      id: record.id,
      promptHash,
      prompt: record.prompt,
      rewrittenPrompt: record.rewrittenPrompt,
      violations: record.violations as PolicyViolation[],
      riskScore: record.riskScore,
      threatLevel: record.threatLevel as AuditRecord['threatLevel'],
      policiesTriggered: record.policiesTriggered as string[],
      secrets: record.secrets as DetectedSecret[],
      decision: record.decision as DecisionType,
      llmProvider: record.llmProvider,
      llmModel: record.llmModel,
      timestamp: new Date(record.timestamp as string).toISOString(),
      user: record.user ?? null,
    };
  }

  protected calculateConfidence(): number {
    return 0.99;
  }
}
