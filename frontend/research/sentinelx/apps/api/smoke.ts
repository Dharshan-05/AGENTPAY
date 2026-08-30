import { detectSecrets } from './src/engines/detectors';
import { evaluatePolicies } from './src/engines/policies';
import { assessRisk } from './src/engines/risk';
import { rewritePrompt } from './src/engines/rewriter';
import { InspectorAgent } from './src/agents/inspector';

async function main() {
  const prompt =
    'Summarize this HR salary sheet: John Carter, EMP-2041, salary 85000 INR/month, email john.carter@acme-corp.com, phone +91-98765-43210.';

  const secrets = detectSecrets(prompt);
  console.log(
    'SECRETS:',
    JSON.stringify(
      secrets.map((s) => ({ type: s.type, label: s.label, match: s.match, redacted: s.redacted, severity: s.severity })),
      null,
      1,
    ),
  );

  const violations = evaluatePolicies(secrets);
  console.log(
    '\nVIOLATIONS:',
    JSON.stringify(
      violations.map((v) => ({ policy: v.policyName, regulation: v.regulation, severity: v.severity })),
      null,
      1,
    ),
  );

  const inspector = await new InspectorAgent().run(prompt);
  const risk = assessRisk({ secrets, violations, inspector: inspector.output });
  console.log('\nRISK:', risk.score, risk.threatLevel, 'confidence:', risk.confidence);
  console.log('IMPACT:', risk.businessImpact.slice(0, 100));

  const rew = rewritePrompt(prompt, secrets);
  console.log('\nREWRITTEN:', rew.rewritten);

  const safe = detectSecrets('Write a haiku about cloud security');
  console.log('\nSAFE PROMPT secrets:', safe.length);

  const card = detectSecrets('My card is 4532 7890 1234 5678');
  console.log('CARD:', card.map((s) => s.label));

  const aws = detectSecrets('aws_access_key_id = AKIAIOSFODNN7EXAMPLE');
  console.log('AWS:', aws.map((s) => s.label + ' / ' + s.severity));
}

main();
