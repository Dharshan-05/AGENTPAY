import type { DetectedSecret, SecretCategoryType, SeverityLevel } from '../lib/types';

import { SecretCategory, Severity } from '../lib/types';


interface DetectionRule {
  type: SecretCategoryType;
  label: string;
  pattern: RegExp;
  severity: SeverityLevel;
  confidence: number;
  description: string;
  redact: (match: string) => string;
}

const star = (match: string, visible = 4) =>
  `${match.slice(0, visible)}${'*'.repeat(Math.max(4, match.length - visible))}`;

const genericRedact = (match: string) => star(match);

export const DETECTION_RULES: DetectionRule[] = [
  {
    type: SecretCategory.GOOGLE_API_KEY,
    label: 'Google API Key',
    pattern: /\bAIza[0-9A-Za-z\-_]{33,35}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.99,
    description: 'Google Cloud API key (AIza prefix, 39 chars)',
    redact: genericRedact,
  },
  {
    type: SecretCategory.AWS_CREDENTIAL,
    label: 'AWS Access Key',
    pattern: /\b(?:AKIA|ASIA|AIDA|AROA)[0-9A-Z]{16}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.98,
    description: 'AWS access key ID (AKIA prefix)',
    redact: genericRedact,
  },
  {
    type: SecretCategory.AWS_CREDENTIAL,
    label: 'AWS Secret Access Key',
    pattern: /\baws_secret_access_key\s*=\s*['"][A-Za-z0-9/+=]{40}['"]/g,
    severity: Severity.CRITICAL,
    confidence: 0.99,
    description: 'AWS secret access key value',
    redact: (m) => m.replace(/[A-Za-z0-9/+=]{40}/, genericRedact),
  },
  {
    type: SecretCategory.AZURE_CREDENTIAL,
    label: 'Azure Storage Key',
    pattern: /DefaultEndpointsProtocol=https;AccountName=[\w-]+;AccountKey=[A-Za-z0-9+/=]{80,}/g,
    severity: Severity.CRITICAL,
    confidence: 0.97,
    description: 'Azure storage account connection string',
    redact: (m) => m.replace(/AccountKey=[A-Za-z0-9+/=]{80,}/, 'AccountKey=***REDACTED***'),
  },
  {
    type: SecretCategory.AZURE_CREDENTIAL,
    label: 'Azure Client Secret',
    pattern: /\b(?:client|app)_secret\s*[:=]\s*['"][A-Za-z0-9_\-~]{30,40}['"]/gi,
    severity: Severity.HIGH,
    confidence: 0.9,
    description: 'Azure AD client secret',
    redact: genericRedact,
  },
  {
    type: SecretCategory.GCP_CREDENTIAL,
    label: 'GCP Service Account',
    pattern: /\b"type"\s*:\s*"service_account"\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.98,
    description: 'Google Cloud service account JSON key',
    redact: () => '***GCP-SERVICE-ACCOUNT-REDACTED***',
  },
  {
    type: SecretCategory.API_KEY,
    label: 'Generic API Key',
    pattern: /\b(?:api[_-]?key|apikey|token|secret[_-]?key)\s*[=:]\s*['"]?([A-Za-z0-9_\-\.]{16,64})/gi,
    severity: Severity.HIGH,
    confidence: 0.85,
    description: 'Generic API key assignment pattern',
    redact: (m) => m.replace(/["'][^"']{4,}["']/, '"***"').replace(/([A-Za-z0-9_\-\.]{16,64})$/, '***'),
  },
  {
    type: SecretCategory.OPENAI_KEY,
    label: 'OpenAI API Key',
    pattern: /\bsk-(?:proj-)?[A-Za-z0-9_\-]{20,80}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.99,
    description: 'OpenAI secret key (sk- prefix)',
    redact: genericRedact,
  },
  {
    type: SecretCategory.STRIPE_KEY,
    label: 'Stripe API Key',
    pattern: /\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{16,64}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.99,
    description: 'Stripe secret or publishable key',
    redact: genericRedact,
  },
  {
    type: SecretCategory.GITHUB_TOKEN,
    label: 'GitHub Token',
    pattern: /\bgh[pousr]_[A-Za-z0-9]{36,255}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.99,
    description: 'GitHub personal access token',
    redact: genericRedact,
  },
  {
    type: SecretCategory.SLACK_TOKEN,
    label: 'Slack Token',
    pattern: /\bxox[baprs]-[A-Za-z0-9\-]{10,150}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.99,
    description: 'Slack bot or app token',
    redact: genericRedact,
  },
  {
    type: SecretCategory.JWT,
    label: 'JWT Token',
    pattern: /\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b/g,
    severity: Severity.HIGH,
    confidence: 0.97,
    description: 'JSON Web Token (3-part base64url)',
    redact: genericRedact,
  },
  {
    type: SecretCategory.OAUTH_TOKEN,
    label: 'OAuth Token',
    pattern: /\b(?:Bearer|OAuth|oauth_token)\s+[A-Za-z0-9\-._~+/=]{20,200}\b/g,
    severity: Severity.HIGH,
    confidence: 0.9,
    description: 'OAuth bearer token',
    redact: (m) => m.replace(/[A-Za-z0-9\-._~+/=]{20,200}$/, genericRedact),
  },
  {
    type: SecretCategory.PASSWORD,
    label: 'Password',
    pattern: /\b(?:password|passwd|pwd|pass)\s*[=:]\s*['"][^'"\s]{4,64}['"]/gi,
    severity: Severity.HIGH,
    confidence: 0.82,
    description: 'Plaintext password assignment',
    redact: (m) => m.replace(/['"][^'"\s]{4,64}['"]$/, '***'),
  },
  {
    type: SecretCategory.PASSWORD,
    label: 'Database Password',
    pattern: /(?:password|pwd)\s*=\s*["'][^"';\s]+["']/gi,
    severity: Severity.HIGH,
    confidence: 0.85,
    description: 'Database connection password parameter',
    redact: (m) => m.replace(/["'][^"';\s]+["']$/, '"***"'),
  },
  {
    type: SecretCategory.SSH_KEY,
    label: 'SSH Private Key',
    pattern: /-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]{0,2000}?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/g,
    severity: Severity.CRITICAL,
    confidence: 0.99,
    description: 'SSH/OpenSSH private key block',
    redact: () => '***SSH-PRIVATE-KEY-REDACTED***',
  },
  {
    type: SecretCategory.PEM_CERT,
    label: 'PEM Certificate',
    pattern: /-----BEGIN CERTIFICATE-----[\s\S]{0,2000}?-----END CERTIFICATE-----/g,
    severity: Severity.HIGH,
    confidence: 0.98,
    description: 'X.509 PEM certificate',
    redact: () => '***PEM-CERTIFICATE-REDACTED***',
  },
  {
    type: SecretCategory.PRIVATE_KEY,
    label: 'Private Key File',
    pattern: /-----BEGIN (?:RSA )?PRIVATE KEY-----/g,
    severity: Severity.CRITICAL,
    confidence: 0.95,
    description: 'Private key header (any format)',
    redact: () => '***PRIVATE-KEY-REDACTED***',
  },
  {
    type: SecretCategory.DATABASE_URL,
    label: 'PostgreSQL URL',
    pattern: /\bpostgres(?:ql)?(?:s)?:\/\/[^\s"'`]{8,}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.97,
    description: 'PostgreSQL connection string with credentials',
    redact: (m) => m.replace(/\/\/[^@]+@/, '//***:***@'),
  },
  {
    type: SecretCategory.MONGO_URI,
    label: 'MongoDB URI',
    pattern: /\bmongodb(?:\+srv)?:\/\/[^\s"'`]{8,}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.97,
    description: 'MongoDB connection string with credentials',
    redact: (m) => m.replace(/\/\/[^@]+@/, '//***:***@'),
  },
  {
    type: SecretCategory.DATABASE_URL,
    label: 'MySQL URL',
    pattern: /\bmysql:\/\/[^\s"'`]{8,}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.97,
    description: 'MySQL connection string',
    redact: (m) => m.replace(/\/\/[^@]+@/, '//***:***@'),
  },
  {
    type: SecretCategory.SQL_CREDENTIAL,
    label: 'JDBC URL',
    pattern: /\bjdbc:(?:mysql|postgresql|sqlserver):\/\/[^\s"'`]{8,}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.96,
    description: 'JDBC connection string',
    redact: (m) => m.replace(/\/\/[^@]+@/, '//***:***@'),
  },
  {
    type: SecretCategory.CREDIT_CARD,
    label: 'Credit Card Number',
    pattern: /\b(?:\d{4}[- ]?){3}\d{4}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.8,
    description: '16-digit payment card number (Luhn checked at runtime)',
    redact: (m) => `**** ${m.replace(/\s|-/g, '').slice(-4)}`,
  },
  {
    type: SecretCategory.AADHAAR,
    label: 'Aadhaar Number',
    pattern: /\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.85,
    description: 'Indian Aadhaar (12-digit UID)',
    redact: (m) => m.replace(/\d/g, 'X'),
  },
  {
    type: SecretCategory.PAN,
    label: 'PAN Number',
    pattern: /\b[A-Z]{5}[0-9]{4}[A-Z]\b/g,
    severity: Severity.HIGH,
    confidence: 0.8,
    description: 'Indian Permanent Account Number',
    redact: genericRedact,
  },
  {
    type: SecretCategory.SSN,
    label: 'Social Security Number',
    pattern: /\b\d{3}-\d{2}-\d{4}\b/g,
    severity: Severity.CRITICAL,
    confidence: 0.95,
    description: 'US Social Security Number',
    redact: (m) => `***-**-${m.slice(-4)}`,
  },
  {
    type: SecretCategory.EMAIL,
    label: 'Email Address',
    pattern: /(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
    severity: Severity.MEDIUM,
    confidence: 0.92,
    description: 'Personal email address',
    redact: (m) => {
      const [user, domain] = m.split('@');
      return `${user[0]}***@${domain}`;
    },
  },
  {
    type: SecretCategory.PHONE,
    label: 'Phone Number',
    pattern: /(?<![0-9])(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g,
    severity: Severity.MEDIUM,
    confidence: 0.85,
    description: 'Phone number (US format)',
    redact: (m) => m.replace(/[\d]/g, (d, i) => (i < m.length - 4 ? 'X' : d)),
  },
  {
    type: SecretCategory.PHONE,
    label: 'Phone Number (5-5 format)',
    pattern: /(?<![0-9])\+?\d{1,3}[-.\s]?\d{5}[-.\s]?\d{5}\b/g,
    severity: Severity.MEDIUM,
    confidence: 0.9,
    description: 'Phone number (international 5-5 format)',
    redact: (m) => m.replace(/[\d]/g, (d, i) => (i < m.length - 4 ? 'X' : d)),
  },
  {
    type: SecretCategory.EMPLOYEE_ID,
    label: 'Employee ID',
    pattern: /\b(?:emp(?:loyee)?[_-]?id|eid|staff[_-]?id)\s*[=:]\s*['"]?[A-Za-z0-9_-]{4,20}/gi,
    severity: Severity.MEDIUM,
    confidence: 0.8,
    description: 'Internal employee identifier',
    redact: genericRedact,
  },
  {
    type: SecretCategory.EMPLOYEE_ID,
    label: 'Employee ID (short form)',
    pattern: /\b(?:EMP|EID|EMPID)[-_]?\d{2,6}\b/gi,
    severity: Severity.MEDIUM,
    confidence: 0.9,
    description: 'Internal employee identifier (EMP-1234 format)',
    redact: (m) => m.replace(/\d+/g, 'XXXX'),
  },
  {
    type: SecretCategory.INTERNAL_URL,
    label: 'Internal URL',
    pattern: /\b(?:https?:\/\/)?(?:[a-z0-9-]+\.)*(?:\.corp|intranet|localhost|.local|.lan|.internal|.corp\b)(?::\d+)?(?:\/[^\s"'`]*)?/gi,
    severity: Severity.LOW,
    confidence: 0.75,
    description: 'Internal network URL or hostname',
    redact: () => '***INTERNAL-URL***',
  },
  {
    type: SecretCategory.IP_ADDRESS,
    label: 'Internal IP Address',
    pattern: /\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}|192\.168\.\d{1,3})\.\d{1,3}\b/g,
    severity: Severity.LOW,
    confidence: 0.9,
    description: 'RFC 1918 private IP address',
    redact: () => '***.*.*.***',
  },
  {
    type: SecretCategory.IBAN,
    label: 'IBAN',
    pattern: /\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b/g,
    severity: Severity.HIGH,
    confidence: 0.8,
    description: 'International Bank Account Number',
    redact: genericRedact,
  },
  {
    type: SecretCategory.SWIFT,
    label: 'SWIFT / BIC Code',
    pattern: /\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b/g,
    severity: Severity.HIGH,
    confidence: 0.7,
    description: 'SWIFT bank identifier',
    redact: genericRedact,
  },
  {
    type: SecretCategory.BITCOIN,
    label: 'Bitcoin Address',
    pattern: /\b(?:bc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{8,87}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b/g,
    severity: Severity.HIGH,
    confidence: 0.9,
    description: 'Bitcoin wallet address',
    redact: genericRedact,
  },
  {
    type: SecretCategory.SOURCE_CODE,
    label: 'Source Code',
    pattern: /\b(?:const|let|var|function|class|def|import)\s+[A-Za-z_$][\w$]*\s*(?:=|=>|\{|\([^)]*\)\s*\{)/g,
    severity: Severity.MEDIUM,
    confidence: 0.7,
    description: 'Embedded source code snippet',
    redact: () => '***SOURCE-CODE***',
  },
  {
    type: SecretCategory.SALARY,
    label: 'Salary / Compensation Data',
    pattern: /\b(?:salary|ctc|compensation|payslip)\b.{0,12}?(?:[$₹€£]\s?)?\d{3,}(?:,\d{3})*(?:[Kk]|[Mm]| INR| USD| EUR)?/gi,
    severity: Severity.HIGH,
    confidence: 0.8,
    description: 'Salary or compensation figure',
    redact: (m) => m.replace(/\d{3,}(?:,\d{3})*(?:[Kk]|[Mm]| INR| USD| EUR)?/g, '***'),
  },
  {
    type: SecretCategory.HEALTH_RECORD,
    label: 'Health / Medical Data',
    pattern: /\b(?:diagnos|medical record|patient|prescription|blood group|hypersensitive|disease|surgery)\b.{0,60}/gi,
    severity: Severity.HIGH,
    confidence: 0.75,
    description: 'Protected health information (HIPAA)',
    redact: () => '***HEALTH-DATA***',
  },
  {
    type: SecretCategory.FINANCIAL_DOC,
    label: 'Financial Document Data',
    pattern: /\b(?:bank statement|account number|transaction|credit score|net worth|balance|invoice no)\b.{0,50}/gi,
    severity: Severity.HIGH,
    confidence: 0.75,
    description: 'Financial document content',
    redact: () => '***FINANCIAL-DATA***',
  },
  {
    type: SecretCategory.LEGAL_DOC,
    label: 'Legal / Confidential Doc',
    pattern: /\b(?:confidential|non-disclosure|nda|legal|court|lawsuit|trade secret|attorney|privileged)\b/gi,
    severity: Severity.HIGH,
    confidence: 0.7,
    description: 'Legally protected document content',
    redact: () => '***LEGAL-DATA***',
  },
  {
    type: SecretCategory.PII,
    label: 'Name (person reference)',
    pattern: /\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}/g,
    severity: Severity.LOW,
    confidence: 0.6,
    description: 'Personal name reference',
    redact: (m) => m.replace(/(?<=Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+/g, ' [NAME]'),
  },
];

const SEVERITY_RANK: Record<string, number> = {
  CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4,
};

function severityRank(s: SeverityLevel): number {
  return SEVERITY_RANK[s] ?? 5;
}

function luhnValid(digits: string): boolean {
  let sum = 0;
  let alt = false;
  for (let i = digits.length - 1; i >= 0; i--) {
    let n = digits.charCodeAt(i) - 48;
    if (alt) {
      n *= 2;
      if (n > 9) n -= 9;
    }
    sum += n;
    alt = !alt;
  }
  return sum % 10 === 0;
}

export function detectSecrets(input: string): DetectedSecret[] {
  const found: DetectedSecret[] = [];
  const seen = new Set<string>();

  for (const rule of DETECTION_RULES) {
    rule.pattern.lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = rule.pattern.exec(input)) !== null) {
      const value = match[0];

      let cardConfidence: number | null = null;
      if (rule.type === SecretCategory.CREDIT_CARD) {
        const digits = value.replace(/[\s-]/g, '');
        if (digits.length !== 16 || !luhnValid(digits)) {
          if (digits.length === 16) {
            cardConfidence = 0.3;
          } else {
            rule.pattern.lastIndex = match.index + 1;
            continue;
          }
        }
      }

      const dedupeKey = `${rule.type}:${value.slice(0, 24)}`;
      if (seen.has(dedupeKey)) {
        rule.pattern.lastIndex = match.index + 1;
        continue;
      }
      seen.add(dedupeKey);

      found.push({
        type: rule.type,
        label: rule.label,
        match: value.length > 120 ? `${value.slice(0, 120)}…` : value,
        redacted: rule.redact(value),
        position: { start: match.index, end: match.index + value.length },
        severity: rule.severity,
        confidence: cardConfidence ?? rule.confidence,
      });

      if (rule.pattern.global) {
        rule.pattern.lastIndex = match.index + 1;
      } else break;
    }
  }

  return found
    .sort((a, b) => a.position.start - b.position.start || b.position.end - a.position.end)
    .reduce<DetectedSecret[]>((acc, s) => {
      const last = acc[acc.length - 1];
      if (last && s.position.start < last.position.end) {
        const longer = s.position.end - s.position.start > last.position.end - last.position.start;
        if (severityRank(s.severity) < severityRank(last.severity) || (s.severity === last.severity && longer)) {
          acc[acc.length - 1] = s;
        }
        return acc;
      }
      acc.push(s);
      return acc;
    }, []);
}

export function getWorstSeverity(secrets: DetectedSecret[]): SeverityLevel {
  const order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO];
  for (const level of order) {
    if (secrets.some((s) => s.severity === level)) return level;
  }
  return Severity.INFO;
}
