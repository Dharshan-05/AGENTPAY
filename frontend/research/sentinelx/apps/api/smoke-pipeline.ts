import { SentinelPipeline } from './src/agents/pipeline';

async function main() {
  const pipeline = new SentinelPipeline();

  const cases = [
    'Summarize this HR salary sheet: John Carter, EMP-2041, salary 85000 INR/month, email john.carter@acme-corp.com, phone +91-98765-43210.',
    'Here is my credit card: 4532 7890 1234 5678, expiry 09/28, CVV 321. Please book a flight.',
    'Write a marketing email announcing our new product launch for Q3. Keep it professional.',
    'Debug this code: const apiKey = "AIzaSyD9cW8jP4fZ2vE3rT6yU1iL0kM7nB5qXvS8";',
    'Can you review our client contract with TechNova for clause 7? It contains attorney-client privileged content.',
    'Extract customer PII: priya.sharma@gmail.com, 91-9988776655.',
    'Compare our AWS deployment config: AKIAIOSFODNN7EXAMPLE with staging at 192.168.1.45.',
    'Analyze patient data: patient A-2231 diagnosed with hypertension, prescribed Metformin 500mg.',
  ];

  for (const prompt of cases) {
    const r = await pipeline.execute(prompt, { provider: 'ollama' });
    console.log('\n' + '='.repeat(100));
    console.log('PROMPT:', prompt.slice(0, 90));
    console.log('DECISION:', r.decision, '| RISK:', r.riskScore, r.threatLevel, '| SECRETS:', r.secrets.length, '| VIOLATIONS:', r.violations.length, '| AGENTS:', r.agentTrace.length, '| LATENCY:', r.latencyMs + 'ms');
    console.log('REWRITTEN:', r.rewrittenPrompt);
    const trace = r.agentTrace.map((a) => `${a.agent}:${a.status}`).join(' -> ');
    console.log('TRACE:', trace);
  }
}

main();
