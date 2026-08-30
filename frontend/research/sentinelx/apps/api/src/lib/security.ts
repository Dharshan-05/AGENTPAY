/**
 * PHASE 6 + 7 — Security Enforcement and Prompt Optimization
 *
 * This module executes the security pipeline BEFORE an LLM provider is called.
 * It enforces PII redaction, secret blocking, and prompt injection blocking.
 * It also applies deterministic token optimization.
 */

import { estimateTokens } from '../llm/tokens';
import type { ChatMessage } from '../llm/providers';

// ── Types ────────────────────────────────────────────────────────────────────
export type FindingType = 'SECRET' | 'PII' | 'PROMPT_INJECTION';
export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type Action = 'ALLOW' | 'REDACT' | 'BLOCK';

export interface SecurityFinding {
  type: FindingType;
  severity: Severity;
  action: Action;
  label: string;
}

export interface SecurityDecision {
  decision: 'ALLOW' | 'REDACT' | 'REWRITE' | 'BLOCK';
  riskScore: number;
  findings: SecurityFinding[];
  originalTokenEstimate: number;
  sanitizedTokenEstimate: number;
  sanitizedMessages: ChatMessage[];
}

export interface OptimizationResult {
  messages: ChatMessage[];
  originalTokens: number;
  optimizedTokens: number;
  tokensSaved: number;
  reductionPercentage: number;
}

// ── 1. Detectors ─────────────────────────────────────────────────────────────

const SECRET_PATTERNS = [
  { label: 'AWS Access Key',      pattern: /AKIA[0-9A-Z]{16}/g, severity: 'CRITICAL' as Severity },
  { label: 'AWS Secret Key',      pattern: /aws.{0,20}secret.{0,20}[0-9a-zA-Z/+=]{40}/gi, severity: 'CRITICAL' as Severity },
  { label: 'GitHub Token',        pattern: /ghp_[a-zA-Z0-9]{36}/gi, severity: 'CRITICAL' as Severity },
  { label: 'OpenAI Key',          pattern: /sk-[a-zA-Z0-9]{48}/gi, severity: 'CRITICAL' as Severity },
  { label: 'OpenRouter Key',      pattern: /sk-or-v1-[a-zA-Z0-9]{64}/gi, severity: 'CRITICAL' as Severity },
  { label: 'Generic Bearer Token',pattern: /bearer\s+[a-zA-Z0-9._\-]{20,}/gi, severity: 'HIGH' as Severity },
];

const PII_PATTERNS = [
  { label: 'Email address', pattern: /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, severity: 'MEDIUM' as Severity },
  { label: 'Phone number',  pattern: /\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b/g, severity: 'MEDIUM' as Severity },
  { label: 'Credit Card',   pattern: /\b(?:4[0-9]{12}|5[1-5][0-9]{14}|3[47][0-9]{13})\b/g, severity: 'HIGH' as Severity },
  { label: 'SSN',           pattern: /\b\d{3}-\d{2}-\d{4}\b/g, severity: 'HIGH' as Severity },
];

const PROMPT_INJECTION_PATTERNS = [
  { label: 'Ignore instructions', pattern: /ignore (all )?(previous )?instructions/gi, severity: 'HIGH' as Severity },
  { label: 'System prompt extraction', pattern: /(reveal|what is|print|output|show) (the|your) (system prompt|core instructions)/gi, severity: 'HIGH' as Severity },
  { label: 'Jailbreak Attempt', pattern: /(you are now (unbound|free|god|dan)|do anything now|enter god mode)/gi, severity: 'CRITICAL' as Severity },
  { label: 'Tool override', pattern: /override (tool|function|safety)/gi, severity: 'HIGH' as Severity },
  { label: 'Credential Exfiltration', pattern: /(provide|show|reveal|give|print).*(credentials|passwords|secrets)/gi, severity: 'CRITICAL' as Severity },
];

// ── 2. Security Pipeline ─────────────────────────────────────────────────────

export function enforceSecurityPolicy(messages: ChatMessage[]): SecurityDecision {
  const originalTokenEstimate = estimateTokens(messages);
  const findings: SecurityFinding[] = [];
  
  let totalRisk = 0;
  let hasBlock = false;
  let hasRedact = false;

  const sanitizedMessages = messages.map(msg => {
    let sanitizedContent = msg.content;

    // Detect Secrets (BLOCK policy)
    for (const rule of SECRET_PATTERNS) {
      const matches = [...sanitizedContent.matchAll(rule.pattern)];
      if (matches.length > 0) {
        findings.push({ type: 'SECRET', severity: rule.severity, action: 'BLOCK', label: rule.label });
        totalRisk += (rule.severity === 'CRITICAL' ? 50 : 30) * matches.length;
        hasBlock = true;
      }
    }

    // Detect Prompt Injection (BLOCK policy)
    for (const rule of PROMPT_INJECTION_PATTERNS) {
      const matches = [...sanitizedContent.matchAll(rule.pattern)];
      if (matches.length > 0) {
        findings.push({ type: 'PROMPT_INJECTION', severity: rule.severity, action: 'BLOCK', label: rule.label });
        totalRisk += (rule.severity === 'CRITICAL' ? 40 : 25) * matches.length;
        hasBlock = true;
      }
    }

    // Detect PII (REDACT policy)
    for (const rule of PII_PATTERNS) {
      while (rule.pattern.exec(sanitizedContent) !== null) {
        findings.push({ type: 'PII', severity: rule.severity, action: 'REDACT', label: rule.label });
        totalRisk += (rule.severity === 'HIGH' ? 20 : 10);
        hasRedact = true;
      }
      sanitizedContent = sanitizedContent.replace(rule.pattern, `[REDACTED_${rule.label.toUpperCase().replace(/ /g, '_')}]`);
    }

    return { ...msg, content: sanitizedContent };
  });

  const riskScore = Math.min(Math.round(totalRisk), 100);
  let decision: SecurityDecision['decision'] = 'ALLOW';
  
  if (hasBlock) {
    decision = 'BLOCK';
  } else if (hasRedact) {
    decision = 'REDACT';
  }

  const sanitizedTokenEstimate = decision === 'BLOCK' ? 0 : estimateTokens(sanitizedMessages);

  return {
    decision,
    riskScore,
    findings,
    originalTokenEstimate,
    sanitizedTokenEstimate,
    sanitizedMessages
  };
}

// ── 3. Prompt Optimization ───────────────────────────────────────────────────

export function optimizePrompt(messages: ChatMessage[]): OptimizationResult {
  const originalTokens = estimateTokens(messages);
  
  const optimizedMessages = messages.map(msg => {
    let optimizedContent = msg.content;
    
    // Only optimize user/system messages. We don't touch strict formatting for tools unless safely identifiable.
    // 1. Remove redundant whitespace (preserve semantic newlines)
    optimizedContent = optimizedContent.replace(/[ \t]{2,}/g, ' ');
    // 2. Normalize excessive line breaks (more than 2 -> 2)
    optimizedContent = optimizedContent.replace(/\n{3,}/g, '\n\n');
    // 3. Trim
    optimizedContent = optimizedContent.trim();
    
    return { ...msg, content: optimizedContent };
  });

  const optimizedTokens = estimateTokens(optimizedMessages);
  const tokensSaved = originalTokens - optimizedTokens;
  const reductionPercentage = originalTokens > 0 ? (tokensSaved / originalTokens) * 100 : 0;

  return {
    messages: optimizedMessages,
    originalTokens,
    optimizedTokens,
    tokensSaved,
    reductionPercentage
  };
}
