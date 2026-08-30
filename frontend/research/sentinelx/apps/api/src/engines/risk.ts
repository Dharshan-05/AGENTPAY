import type { DetectedSecret, InspectorOutput, PolicyViolation, RiskAssessment, SeverityLevel, ThreatLevelType } from '../lib/types';

import { Severity, ThreatLevel } from '../lib/types';


interface RiskInput {
  secrets: DetectedSecret[];
  violations: PolicyViolation[];
  inspector: InspectorOutput;
  historicalRisk?: number;
  historyCount?: number;
}

const SEVERITY_WEIGHT: Record<SeverityLevel, number> = {
  CRITICAL: 40,
  HIGH: 25,
  MEDIUM: 12,
  LOW: 5,
  INFO: 1,
};

export function assessRisk(input: RiskInput): RiskAssessment {
  const { secrets, violations, inspector, historicalRisk = 15, historyCount = 0 } = input;

  const factors: RiskAssessment['contributingFactors'] = [];

  let score = 0;

  if (secrets.length > 0) {
    const worst = secrets.reduce<number>(
      (acc, s) => Math.max(acc, SEVERITY_WEIGHT[s.severity]),
      0,
    );
    const rawSecretScore = worst * (1 + Math.min(secrets.length - 1, 5) * 0.15);
    factors.push({
      factor: `${secrets.length} sensitive entit${secrets.length === 1 ? 'y' : 'ies'} detected (${secrets.map((s) => s.label).slice(0, 3).join(', ')}${secrets.length > 3 ? '…' : ''})`,
      weight: Math.min(rawSecretScore, 55),
      severity: worst >= SEVERITY_WEIGHT.CRITICAL ? Severity.CRITICAL : worst >= SEVERITY_WEIGHT.HIGH ? Severity.HIGH : Severity.MEDIUM,
    });
    score += Math.min(rawSecretScore, 55);
  }

  if (violations.length > 0) {
    const violationScore = violations.reduce((acc, v) => acc + SEVERITY_WEIGHT[v.severity] * 1.2, 0);
    factors.push({
      factor: `${violations.length} policy violation${violations.length === 1 ? '' : 's'} (${[...new Set(violations.map((v) => v.regulation))].join(', ')})`,
      weight: Math.min(violationScore, 60),
      severity: violations[0].severity,
    });
    score += Math.min(violationScore, 60);
  }

  const sensitivityWeight = Math.min(inspector.dataSensitivity * 0.15, 15);
  if (inspector.dataSensitivity > 3) {
    factors.push({
      factor: `Prompt classified as ${sensitivityLabel(inspector.dataSensitivity)} sensitivity`,
      weight: sensitivityWeight,
      severity: Severity.MEDIUM,
    });
    score += sensitivityWeight;
  }

  const intentPenalty = intentRisk(inspector.intent);
  if (intentPenalty > 0) {
    factors.push({
      factor: `Prompt intent suggests ${inspector.intent.toLowerCase()} activity`,
      weight: intentPenalty,
      severity: Severity.HIGH,
    });
    score += intentPenalty;
  }

  if (historyCount > 0 && historicalRisk > 40) {
    const historyWeight = Math.min(historicalRisk * 0.15, 12);
    factors.push({
      factor: `User's historical risk elevated (${Math.round(historicalRisk)}/100, ${historyCount} prior events)`,
      weight: historyWeight,
      severity: Severity.MEDIUM,
    });
    score += historyWeight;
  }

  score = Math.min(100, Math.round(score));

  const threatLevel = score >= 80 ? ThreatLevel.CRITICAL : score >= 60 ? ThreatLevel.HIGH : score >= 35 ? ThreatLevel.MEDIUM : score >= 15 ? ThreatLevel.LOW : ThreatLevel.SAFE;

  const confidence = secrets.length > 0 || violations.length > 0
    ? Math.min(0.99, 0.75 + secrets.length * 0.04 + violations.length * 0.02)
    : Math.min(0.8, 0.4 + inspector.dataSensitivity * 0.05);

  return {
    score,
    threatLevel,
    confidence: Math.round(confidence * 100) / 100,
    businessImpact: impactFor(threatLevel),
    contributingFactors: factors.sort((a, b) => b.weight - a.weight),
    recommendation: recommendationFor(threatLevel),
  };
}

function sensitivityLabel(n: number): string {
  if (n >= 8) return 'extreme';
  if (n >= 6) return 'high';
  if (n >= 4) return 'elevated';
  return 'moderate';
}

function intentRisk(intent: string): number {
  const i = intent.toLowerCase();
  if (/(summar|analyse|analyze|review)/.test(i) && /(salary|compensation|payroll|finance|hr)/.test(i)) return 10;
  if (/(extract|retrieve|exfiltrat|scrape|download)/.test(i)) return 18;
  if (/(privat|secret|password|credential|token|key)/.test(i)) return 15;
  return 0;
}

function impactFor(threatLevel: ThreatLevelType): string {
  if (threatLevel === ThreatLevel.CRITICAL)
    return 'Critical regulatory exposure — potential reportable breach (GDPR Art. 33 / HIPAA breach notification) with fines up to €20M or 4% of global turnover.';
  if (threatLevel === ThreatLevel.HIGH)
    return 'High business impact — credential compromise could enable lateral movement and data exfiltration.';
  if (threatLevel === ThreatLevel.MEDIUM)
    return 'Moderate impact — potential privacy complaint, audit finding, or reputational damage.';
  if (threatLevel === ThreatLevel.LOW)
    return 'Limited impact — low sensitivity data, minor exposure.';
  return 'No measurable business impact — benign traffic.';
}

function recommendationFor(threatLevel: ThreatLevelType): string {
  if (threatLevel === ThreatLevel.CRITICAL)
    return 'BLOCK the request. Revoke affected credentials, notify the security team, and open an incident ticket.';
  if (threatLevel === ThreatLevel.HIGH)
    return 'Block or rewrite with full redaction. Require explicit manager approval for transmission.';
  if (threatLevel === ThreatLevel.MEDIUM)
    return 'Rewrite the prompt to remove sensitive entities, then allow with logging.';
  if (threatLevel === ThreatLevel.LOW)
    return 'Flag for review; allow after sanitisation.';
  return 'Allow. No action required.';
}
