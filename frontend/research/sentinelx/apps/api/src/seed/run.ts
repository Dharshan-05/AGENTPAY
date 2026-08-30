import bcrypt from 'bcryptjs';
import { store } from '../lib/store';
import { POLICY_PACKS } from '../engines/policies';
import { DETECTION_RULES } from '../engines/detectors';
import { SentinelPipeline } from '../agents/pipeline';

const DEMO_PROMPTS = [
  {
    prompt:
      'Summarize this HR salary sheet: John Carter, EMP-2041, salary 85000 INR/month, email john.carter@acme-corp.com, phone +91-98765-43210.',
    provider: 'ollama',
  },
  {
    prompt:
      'Extract customer PII from this file: priya.sharma@gmail.com, 91-9988776655, Mumbai, account balance ₹4,20,000.',
    provider: 'openai',
  },
  {
    prompt:
      'Write a marketing email announcing our new product launch for Q3. Keep it professional.',
    provider: 'gemini',
  },
  {
    prompt:
      'Debug this code snippet: const apiKey = "AIzaSyD9cW8jP4fZ2vE3rT6yU1iL0kM7nB5qXvS8"; function fetchData() { return fetch(apiKey); }',
    provider: 'openai',
  },
  {
    prompt:
      'Can you review our client contract with TechNova for clause 7 about liability limits? It mentions attorney-client privileged content.',
    provider: 'claude',
  },
  {
    prompt:
      'Compare our AWS deployment config: AKIAIOSFODNN7EXAMPLE with the staging environment at 192.168.1.45.',
    provider: 'openai',
  },
  {
    prompt:
      'Draft a response to customer Sarah Mitchell regarding invoice INV-88912 for $1,250.30 due on 2026-08-15. Her email sarah.mitchell@client-firm.com.',
    provider: 'openai',
  },
  {
    prompt:
      'Help me write SQL for our employees table: SELECT * FROM employees WHERE employee_id = EMP-7789 AND password = "SecurePass!2026";',
    provider: 'ollama',
  },
  {
    prompt: 'Explain the benefits of REST API design patterns in 5 bullet points.',
    provider: 'openrouter',
  },
  {
    prompt:
      'Analyze our patient data for Q2: patient A-2231 diagnosed with hypertension, prescribed Metformin 500mg, blood group O+.',
    provider: 'openai',
  },
  {
    prompt:
      'Summarize the Q1 financial report: revenue grew 12%, total assets $45M, company EBITDA $8.2M. Include the SWIFT code ICICINBBCTS and account details for wire transfers.',
    provider: 'gemini',
  },
  {
    prompt: 'Suggest names for our new AI security product.',
    provider: 'openai',
  },
  {
    prompt:
      'Here is my credit card: 4242 4242 4242 4242, expiry 09/28, CVV 321. Please book a flight.',
    provider: 'claude',
  },
  {
    prompt:
      'Share this employee compensation document with the finance team: Ramesh Kumar, EMP-8821, CTC 24 LPA, payslip attached, PAN ABCDE1234F, Aadhaar 2345 6789 0123.',
    provider: 'openai',
  },
  {
    prompt: 'What are the best practices for prompt injection defense?',
    provider: 'openrouter',
  },
];

export async function runSeed(): Promise<void> {
  console.log('🌱 Seeding SentinelX database...');

  const hashed = await bcrypt.hash('SentinelX2024!', 10);
  const user = await store.user.upsert({
    where: { email: 'demo@sentinelx.dev' },
    update: {},
    create: {
      email: 'demo@sentinelx.dev',
      name: 'Aarav Mehta',
      role: 'SECURITY_ADMIN',
      department: 'Security Operations',
      password: hashed,
    },
  });

  const users = await Promise.all(
    [
      ['priya.sharma@acme-corp.com', 'Priya Sharma', 'EMPLOYEE', 'Finance'],
      ['ravi.patel@acme-corp.com', 'Ravi Patel', 'EMPLOYEE', 'Engineering'],
      ['sneha.iyer@acme-corp.com', 'Sneha Iyer', 'EMPLOYEE', 'Human Resources'],
      ['arjun.nair@acme-corp.com', 'Arjun Nair', 'SECURITY_ANALYST', 'Security Operations'],
      ['kavya.reddy@acme-corp.com', 'Kavya Reddy', 'EMPLOYEE', 'Sales'],
    ].map(([email, name, role, department]) =>
      store.user.upsert({
        where: { email },
        update: {},
        create: { email, name, role, department, password: hashed },
      }),
    ),
  );

  const policyCount = await store.policy.count();
  if (policyCount === 0) {
    await store.policy.createMany({
      data: POLICY_PACKS.map((pack) => ({
        name: pack.name,
        description: pack.description,
        regulation: pack.regulation,
        category: pack.category,
        severity: pack.severity,
        rules: pack.rules,
        enabled: true,
      })),
    });
    console.log(`   ${POLICY_PACKS.length} policy packs created`);
  }

  const ruleCount = await store.detectionRule.count();
  if (ruleCount === 0) {
    await store.detectionRule.createMany({
      data: DETECTION_RULES.map((rule) => ({
        name: rule.label,
        category: rule.type,
        pattern: rule.pattern.source,
        severity: rule.severity,
        description: rule.description,
        enabled: true,
      })),
    });
    console.log(`   ${DETECTION_RULES.length} detection rules created`);
  }

  const auditCount = await store.auditLog.count();
  if (auditCount === 0) {
    const pipeline = new SentinelPipeline(undefined, { paced: false });
    const allUsers = [user, ...users];
    let i = 0;
    for (const demo of DEMO_PROMPTS) {
      try {
        await pipeline.execute(demo.prompt, {
          userId: allUsers[i % allUsers.length].id,
          provider: demo.provider,
          ipAddress: `10.0.${Math.floor(Math.random() * 5)}.${Math.floor(Math.random() * 200) + 20}`,
        });
      } catch {
        // blocked prompts intentionally
      }
      i++;
    }
    console.log(`   ${DEMO_PROMPTS.length} demo audit records generated`);
  }

  const alertCount = await store.alert.count();
  if (alertCount === 0) {
    await store.alert.createMany({
      data: [
        {
          title: 'AWS credential exposed in prompt',
          description: 'User priya.sharma@acme-corp.com attempted to submit AKIA... credential to OpenAI. Request blocked.',
          severity: 'CRITICAL',
          source: 'secret-detection-agent',
        },
        {
          title: 'GDPR violation: customer PII in prompt',
          description: 'Personal data (email + phone) detected in prompt to Gemini. Request rewritten.',
          severity: 'HIGH',
          source: 'policy-engine',
        },
        {
          title: 'PCI DSS: card number submitted',
          description: '16-digit card number (4532 **** 5678) attempted transmission to Claude. Blocked.',
          severity: 'CRITICAL',
          source: 'policy-engine',
        },
        {
          title: 'Salary data leak attempt',
          description: 'Compensation data submitted to external model. Rewritten per corporate policy §4.2.',
          severity: 'HIGH',
          source: 'risk-engine',
        },
        {
          title: 'Unusual session volume detected',
          description: '12 prompt events in 5 minutes from a single session. Rate limit engaged.',
          severity: 'MEDIUM',
          source: 'memory-agent',
        },
        {
          title: 'PHI detected: patient record',
          description: 'HIPAA-protected health information submitted to OpenAI. Request blocked.',
          severity: 'CRITICAL',
          source: 'inspector-agent',
        },
      ],
    });
    console.log('   6 alerts created');
  }

  const settingCount = await store.setting.count();
  if (settingCount === 0) {
    await store.setting.createMany({
      data: [
        { key: 'risk_threshold_critical', value: '80', category: 'risk' },
        { key: 'risk_threshold_high', value: '60', category: 'risk' },
        { key: 'default_provider', value: 'openai', category: 'gateway' },
        { key: 'default_model', value: 'auto', category: 'gateway' },
        { key: 'rewrite_enabled', value: 'true', category: 'rewriter' },
        { key: 'block_on_critical', value: 'true', category: 'policy' },
        { key: 'retention_days', value: '365', category: 'audit' },
        { key: 'company_name', value: 'Acme Corp', category: 'general' },
      ],
    });
  }

  console.log('✅ Seed complete');
}


