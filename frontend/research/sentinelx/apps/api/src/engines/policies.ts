import type { DetectedSecret, PolicyViolation, SecretCategoryType, SeverityLevel } from '../lib/types';

import { SecretCategory, Severity } from '../lib/types';


export interface PolicyRule {
  id: string;
  description: string;
  severity: SeverityLevel;
  triggersOn: SecretCategoryType[];
  recommendation: string;
  explain: (secret: DetectedSecret) => string;
}

export interface PolicyPack {
  id: string;
  name: string;
  regulation: string;
  category: string;
  description: string;
  severity: SeverityLevel;
  rules: PolicyRule[];
}

const categoryLabel: Record<string, string> = {
  API_KEY: 'API keys',
  OPENAI_KEY: 'OpenAI API keys',
  JWT: 'JWT tokens',
  PASSWORD: 'plaintext passwords',
  AWS_CREDENTIAL: 'AWS credentials',
  AZURE_CREDENTIAL: 'Azure credentials',
  GCP_CREDENTIAL: 'Google Cloud credentials',
  SSH_KEY: 'SSH private keys',
  PEM_CERT: 'PEM certificates',
  PRIVATE_KEY: 'private keys',
  DATABASE_URL: 'database connection strings',
  MONGO_URI: 'MongoDB URIs',
  SQL_CREDENTIAL: 'SQL credentials',
  CREDIT_CARD: 'payment card numbers',
  AADHAAR: 'Aadhaar numbers',
  PAN: 'PAN numbers',
  SSN: 'Social Security numbers',
  EMAIL: 'email addresses',
  PHONE: 'phone numbers',
  EMPLOYEE_ID: 'employee IDs',
  INTERNAL_URL: 'internal URLs',
  OAUTH_TOKEN: 'OAuth tokens',
  IP_ADDRESS: 'internal IP addresses',
  IBAN: 'IBANs',
  SWIFT: 'SWIFT codes',
  BITCOIN: 'cryptocurrency addresses',
  SOURCE_CODE: 'source code',
  SALARY: 'salary data',
  HEALTH_RECORD: 'health records',
  FINANCIAL_DOC: 'financial documents',
  LEGAL_DOC: 'legal documents',
  PII: 'personally identifiable information',
  CODE_SECRET: 'code secrets',
  SESSION_TOKEN: 'session tokens',
  GOOGLE_API_KEY: 'Google API keys',
  STRIPE_KEY: 'Stripe keys',
  GITHUB_TOKEN: 'GitHub tokens',
  SLACK_TOKEN: 'Slack tokens',
};

const ctx = (s: DetectedSecret) => `${s.label} (${categoryLabel[s.type] ?? s.type})`;

const t = (s: DetectedSecret, pack: string, detail: string) => `${pack}: ${ctx(s)} ${detail}`;

const rule = (
  id: string,
  description: string,
  severity: SeverityLevel,
  triggersOn: SecretCategoryType[],
  recommendation: string,
  explain: (s: DetectedSecret) => string,
): PolicyRule => ({ id, description, severity, triggersOn, recommendation, explain });

export const POLICY_PACKS: PolicyPack[] = [
  {
    id: 'pol-gdpr',
    name: 'GDPR Data Protection Pack',
    regulation: 'GDPR',
    category: 'Data Privacy',
    description:
      'Enforces EU General Data Protection Regulation. Blocks personal data (PII) from leaving the organisation via prompts to external models.',
    severity: Severity.HIGH,
    rules: [
      rule(
        'gdpr-art-32',
        'Personal data (PII) must not be transmitted to third-party processors without contractual basis.',
        Severity.HIGH,
        [SecretCategory.EMAIL, SecretCategory.PHONE, SecretCategory.PII, SecretCategory.SSN, SecretCategory.AADHAAR, SecretCategory.PAN],
        'Pseudonymise or redact personal identifiers before transmission. Ensure a Data Processing Agreement exists with the model provider.',
        (s) => t(s, 'GDPR Art. 5(1)(f) & Art. 32', 'is personal data. Transmitting it to an external LLM is a data transfer requiring lawful basis and technical safeguards.'),
      ),
      rule(
        'gdpr-cross-border',
        'Cross-border data transfer of personal data requires adequacy decisions or SCCs.',
        Severity.CRITICAL,
        [SecretCategory.HEALTH_RECORD, SecretCategory.LEGAL_DOC],
        'Route via a European-hosted model or anonymise before sending.',
        (s) => t(s, 'GDPR Chapter V', 'may require explicit transfer safeguards. Keep data in-region or redact fully.'),
      ),
    ],
  },
  {
    id: 'pol-hipaa',
    name: 'HIPAA Privacy Rule Pack',
    regulation: 'HIPAA',
    category: 'Healthcare',
    description:
      'Protects Protected Health Information (PHI) under HIPAA 45 CFR 164.502. Blocks medical and patient data from AI prompts.',
    severity: Severity.CRITICAL,
    rules: [
      rule(
        'hipaa-phi',
        'Protected Health Information must never leave the covered entity.',
        Severity.CRITICAL,
        [SecretCategory.HEALTH_RECORD, SecretCategory.PII, SecretCategory.SSN],
        'Block request. PHI must be processed within the covered entity boundary. Consider on-premises models only.',
        (s) => t(s, 'HIPAA 45 CFR 164.502(a)', 'is Protected Health Information. Transmission to an unapproved model is a reportable breach scenario.'),
      ),
    ],
  },
  {
    id: 'pol-pcidss',
    name: 'PCI DSS Compliance Pack',
    regulation: 'PCI DSS',
    category: 'Payments',
    description:
      'PCI DSS v4.0 Requirement 3: cardholder data must be protected and never stored or transmitted insecurely.',
    severity: Severity.CRITICAL,
    rules: [
      rule(
        'pci-chd',
        'Cardholder data (PAN, CVV, track data) must not be transmitted outside the cardholder data environment (CDE).',
        Severity.CRITICAL,
        [SecretCategory.CREDIT_CARD, SecretCategory.IBAN, SecretCategory.SWIFT],
        'Block request and tokenise cardholder data. Never submit PANs to generative AI services.',
        (s) => t(s, 'PCI DSS Req. 3.2/4.1', 'is cardholder data. Transmission outside the CDE violates scope requirements and could invalidate compliance attestation.'),
      ),
    ],
  },
  {
    id: 'pol-soc2',
    name: 'SOC 2 Security Pack',
    regulation: 'SOC 2',
    category: 'Trust & Security',
    description:
      'SOC 2 Trust Services Criteria (CC6.1, CC7.3): logical access, secret management, and monitoring controls.',
    severity: Severity.HIGH,
    rules: [
      rule(
        'soc2-cc61',
        'Access credentials and secrets must be protected against unauthorised transmission.',
        Severity.CRITICAL,
        [
          SecretCategory.AWS_CREDENTIAL,
          SecretCategory.AZURE_CREDENTIAL,
          SecretCategory.GCP_CREDENTIAL,
          SecretCategory.API_KEY,
          SecretCategory.OPENAI_KEY,
          SecretCategory.STRIPE_KEY,
          SecretCategory.GITHUB_TOKEN,
          SecretCategory.SLACK_TOKEN,
          SecretCategory.OAUTH_TOKEN,
          SecretCategory.JWT,
        ],
        'Rotate the exposed credential immediately and redact it from the prompt. Enable secret scanning in CI/CD.',
        (s) => t(s, 'SOC 2 CC6.1', 'is an access credential. Transmission to an LLM is an unauthorised disclosure of a security control.'),
      ),
      rule(
        'soc2-cc73',
        'System operations must have monitoring and alerting for security events.',
        Severity.MEDIUM,
        [SecretCategory.SOURCE_CODE, SecretCategory.PASSWORD],
        'Sanitise prompt. Log the event for SOC 2 evidence.',
        (s) => t(s, 'SOC 2 CC7.3', 'in prompt content triggers the incident monitoring control. Event logged and alerted.'),
      ),
    ],
  },
  {
    id: 'pol-iso27001',
    name: 'ISO 27001 Controls Pack',
    regulation: 'ISO 27001',
    category: 'Information Security',
    description:
      'ISO/IEC 27001 Annex A (A.9, A.10, A.13): asset protection, cryptography, and communications security.',
    severity: Severity.HIGH,
    rules: [
      rule(
        'iso-a926',
        'Secrets must be removed from systems and transmissions (A.9.2.6, A.10.1.1).',
        Severity.HIGH,
        [
          SecretCategory.SSH_KEY,
          SecretCategory.PEM_CERT,
          SecretCategory.PRIVATE_KEY,
          SecretCategory.PASSWORD,
          SecretCategory.DATABASE_URL,
          SecretCategory.MONGO_URI,
          SecretCategory.SQL_CREDENTIAL,
        ],
        'Redact secret material, revoke exposed keys, and enforce secret hygiene policy.',
        (s) => t(s, 'ISO 27001 A.9.2.6/A.10.1.1', 'must not appear in cleartext outside secured storage. Prompt contains secret material.'),
      ),
      rule(
        'iso-a131',
        'Network and communications security controls (A.13.1).',
        Severity.MEDIUM,
        [SecretCategory.INTERNAL_URL, SecretCategory.IP_ADDRESS],
        'Rewrite prompt to remove internal infrastructure references.',
        (s) => t(s, 'ISO 27001 A.13.1', 'reveals internal network topology. This is a technical vulnerability disclosure.'),
      ),
    ],
  },
  {
    id: 'pol-internal',
    name: 'Internal Corporate Policy',
    regulation: 'ACME-INTERNAL',
    category: 'Corporate',
    description:
      'Company policy: confidential business documents, salary data, and internal identifiers must never be shared with external models.',
    severity: Severity.HIGH,
    rules: [
      rule(
        'corp-salary',
        'Compensation data is confidential per employment contract.',
        Severity.CRITICAL,
        [SecretCategory.SALARY],
        'Block or rewrite to remove compensation details.',
        (s) => t(s, 'Internal policy 4.2', 'is confidential compensation data.'),
      ),
      rule(
        'corp-legal',
        'Legal and board documents are attorney-client privileged.',
        Severity.HIGH,
        [SecretCategory.LEGAL_DOC, SecretCategory.FINANCIAL_DOC],
        'Flag for legal review before transmission.',
        (s) => t(s, 'Internal policy 4.5', 'is privileged material.'),
      ),
      rule(
        'corp-employee',
        'Employee identifiers and HR data must not be processed by external AI.',
        Severity.MEDIUM,
        [SecretCategory.EMPLOYEE_ID, SecretCategory.SALARY],
        'Pseudonymise employee identifiers.',
        (s) => t(s, 'Internal policy 5.1', 'is HR data requiring approval.'),
      ),
      rule(
        'corp-aadhaar',
        'Aadhaar and national identifiers must never leave the network.',
        Severity.CRITICAL,
        [SecretCategory.AADHAAR, SecretCategory.PAN, SecretCategory.SSN],
        'Block immediately and notify the Data Protection Officer.',
        (s) => t(s, 'Internal policy 5.4', 'is a national identifier. Transmission is strictly prohibited.'),
      ),
    ],
  },
  {
    id: 'pol-secrets',
    name: 'Enterprise Secrets Hygiene',
    regulation: 'SEC-ENG-01',
    category: 'Secret Management',
    description:
      'Zero-tolerance policy: any form of credential, key, or token in an AI prompt is a security incident.',
    severity: Severity.HIGH,
    rules: [
      rule(
        'sec-engine-01',
        'No secrets in prompts, ever.',
        Severity.CRITICAL,
        [
          SecretCategory.AWS_CREDENTIAL,
          SecretCategory.AZURE_CREDENTIAL,
          SecretCategory.GCP_CREDENTIAL,
          SecretCategory.API_KEY,
          SecretCategory.OPENAI_KEY,
          SecretCategory.JWT,
          SecretCategory.OAUTH_TOKEN,
          SecretCategory.SSH_KEY,
          SecretCategory.PEM_CERT,
          SecretCategory.PRIVATE_KEY,
          SecretCategory.DATABASE_URL,
          SecretCategory.MONGO_URI,
          SecretCategory.SQL_CREDENTIAL,
          SecretCategory.STRIPE_KEY,
          SecretCategory.GITHUB_TOKEN,
          SecretCategory.SLACK_TOKEN,
          SecretCategory.GOOGLE_API_KEY,
          SecretCategory.SESSION_TOKEN,
          SecretCategory.CODE_SECRET,
        ],
        'Redact secret, revoke and rotate the credential, notify the security team, and document the incident in the audit log.',
        (s) => t(s, 'Enterprise Secrets Hygiene (SEC-ENG-01)', 'was detected. All credential material is prohibited in AI prompts. Treated as a security incident.'),
      ),
    ],
  },
];

const RULES_BY_CATEGORY = new Map<SecretCategoryType, Array<{ pack: PolicyPack; rule: PolicyRule }>>();
for (const pack of POLICY_PACKS) {
  for (const packRule of pack.rules) {
    for (const cat of packRule.triggersOn) {
      const list = RULES_BY_CATEGORY.get(cat) ?? [];
      list.push({ pack, rule: packRule });
      RULES_BY_CATEGORY.set(cat, list);
    }
  }
}

export function evaluatePolicies(secrets: DetectedSecret[]): PolicyViolation[] {
  const violations: PolicyViolation[] = [];
  const seen = new Set<string>();

  for (const secret of secrets) {
    const matched = RULES_BY_CATEGORY.get(secret.type) ?? [];
    for (const { pack, rule } of matched) {
      const key = `${rule.id}:${secret.position.start}`;
      if (seen.has(key)) continue;
      seen.add(key);

      const severity = rule.severity === Severity.HIGH ? severityForSecret(secret, rule.severity) : rule.severity;

      violations.push({
        policyId: pack.id,
        policyName: pack.name,
        regulation: pack.regulation,
        category: pack.category,
        severity,
        ruleId: rule.id,
        reason: rule.explain(secret),
        recommendation: rule.recommendation,
      });
    }
  }

  return violations.sort((a, b) => severityRank(a.severity) - severityRank(b.severity));
}

function severityForSecret(secret: DetectedSecret, ruleSeverity: SeverityLevel): SeverityLevel {
  if (secret.severity === Severity.CRITICAL) return Severity.CRITICAL;
  if (secret.severity === Severity.LOW && ruleSeverity === Severity.HIGH) return Severity.MEDIUM;
  return ruleSeverity;
}

function severityRank(s: SeverityLevel): number {
  return [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO].indexOf(s);
}

export function policyPacksForDisplay() {
  return POLICY_PACKS.map((pack) => ({
    id: pack.id,
    name: pack.name,
    regulation: pack.regulation,
    category: pack.category,
    description: pack.description,
    severity: pack.severity,
    ruleCount: pack.rules.length,
  }));
}
