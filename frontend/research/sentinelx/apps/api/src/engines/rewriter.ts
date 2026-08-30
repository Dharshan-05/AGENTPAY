import type { DetectedSecret } from '../lib/types';


interface RewriteResult {
  rewritten: string;
  redactions: Array<{ original: string; replacement: string }>;
}

const INTENT_PHRASES: Array<{ pattern: RegExp; replacement: string }> = [
  { pattern: /\bsalary\s+sheet\b/gi, replacement: 'employee compensation document' },
  { pattern: /\bpayslips?\b/gi, replacement: 'compensation records' },
  { pattern: /\bpayroll\b/gi, replacement: 'compensation records' },
  { pattern: /\bctc\b/gi, replacement: 'compensation' },
];

export function rewritePrompt(original: string, secrets: DetectedSecret[]): RewriteResult {
  const redactions: RewriteResult['redactions'] = [];
  let rewritten = original;

  for (const secret of secrets) {
    if (!rewritten.includes(secret.match)) continue;
    rewritten = rewritten.replace(secret.match, secret.redacted);
    redactions.push({ original: secret.match, replacement: secret.redacted });
  }

  for (const phrase of INTENT_PHRASES) {
    rewritten = rewritten.replace(phrase.pattern, (match) => {
      redactions.push({ original: match, replacement: phrase.replacement });
      return phrase.replacement;
    });
  }

  rewritten = rewritten.replace(/\b\d{16}\b/g, (m) => {
    redactions.push({ original: m, replacement: '[CARD]' });
    return '[CARD]';
  });

  return { rewritten, redactions };
}
