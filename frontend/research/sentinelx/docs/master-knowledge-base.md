# SentinelX Comprehensive Knowledge Base

## 1. Repository Structure & Configuration
- Forensic audit reveals modular architecture with Next.js frontend and Node.js backend
- Key directories:
  - `/apps/api`: Backend services with NestJS framework
  - `/apps/web`: Next.js frontend application
  - `/migrations`: Prisma database migrations
  - `/_scripts`: Utility scripts
- Critical configuration files:
  - `prisma.schema`: Database schema definition
  - `AGENTS.md`: Agent implementation rules and constraints
  - `vercel.json`: Deployment configuration
  - `next.config.js`: Webpack configuration

## 2. Architecture Overview
### System Components
```
Monolith with Microservices Pattern
├── API Gateway (ExpressJS)
├── Core Services
│   ├── Pipeline Agent
│   ├── Policy Engine
│   ├── Risk Assessment
│   ├── Secret Detection
│   └── Rewrite Engine
├── LLM Integration
│   ├── OpenRouter
│   └── Fallback Implementations
├── Database (PostgreSQL)
│   └── Prisma ORM
└── Authentication
   └── NextAuth
```

## 3. Technology Stack
- **Frontend**: React 18, Next.js 14, TypeScript 5.3
- **Backend**: NestJS 10, ExpressJS, Prisma 4
- **LLMs**: OpenRouter integration with fallback to local models
- **Database**: PostgreSQL 16 with Prisma ORM
- **Auth**: NextAuth.js with JWT
- **Deployment**: Vercel platform
- **Utilities**: Winston logging, Zod validation

## 4. AI Governance Implementation
### Policy Engine (engines/policies.ts)
```typescript
// Policy types
enum PolicyType {
  THREAT_DETECTION = 'threat-detection',
  CONTENT_MODERATION = 'content-moderation',
  COMPLIANCE_CHECK = 'compliance-check',
  ACCESS_CONTROL = 'access-control'
}

interface PolicyRule {
  id: string;
  type: PolicyType;
  severity: 'low'|'medium'|'high';
  description: string;
  action: 'alert'|'block'|'retain';
  conditions: RuleCondition[];
}
```

### Agent Pipeline (apps/api/src/agents/pipeline.ts)
```typescript
const pipeline = createPipeline({
  name: 'sentinel-x',
  steps: [
    { type: 'LLM', name: 'Input Validation' },
    { type: 'Policy', rules: [RuleType.CONTENT_FILTER] },
    { type: 'Threat Detection' },
    { type: 'Rewrite Engine' },
    { type: 'Output Sanitization' }
  ]
});
```

## 5. Security Implementation
### Authentication Flow
```
User -> [Sign In] -> NextAuth
          -> JWT Token Issued
          -> Store in httpOnly Cookie
          -> API Routes check JWT on each request
```

### Secret Detection (engines/secrets.ts)
- Regex patterns for:
  - Credit card numbers
  - API keys (format-based detection)
  - JWT tokens
  - Database credentials

## 6. Database Schema
```prisma
model ScanResult {
  id String @id
  userId String @relation(fields: [userId], references: [id])
  user User @relation(rollups: { count: true })
  scanId String
  timestamp DateTime @default(now())
  input Text
  output Text
  riskScore Float
  policiesMatched String[]
  detectedSecrets Boolean
  actions Taken String[]
}

model PolicyRule {
  id String @id
  name String
  type PolicyType
  severity Severity
  conditions Json
}
```

## 7. OpenRouter Integration
```typescript
// apps/api/src/llm/openrouter.ts
async function getLLMResponse(input: string) {
  try {
    return await openRouterCall(input);
  } catch (error) {
    return fallbackToLocalModel(input);
  }
}

// Fallback implementation
const localModel = createLocalModel({
  modelPath: './models/sentinel-local/model discouragements_ADAPTER lãi rate.json',
  tensorReceiveTimeout: 60000
});

## 8. Deployment Configuration (vercel.json)
{
  "version": 1,
  "includeFiles": ["**/*.ts", "**/*.tsx", "prisma/schema.prisma"],
  "functions": {
    "exclude": ["(.*)/node_modules/*"]
  }
}

## 9. Executive Security Center Implementation
- Dashboard showing:
  - Real-time threat map
  - Policy violation trends
  - Secret detection statistics
  - User access patterns

## 10. Judge Mode (apps/web/src/app/(dashboard)/judge-mode/page.tsx)
- Special UI mode that:
  - Shows detailed threat analysis
  - Provides override capabilities for security alerts
  - Maintains audit trail of human decisions

## 11. Limitations & Known Issues
1. Simulation: Some threat detection signatures are placeholder patterns
2. Configuration-dependent: Many features require API keys in .env
3. Deployment constraints: Vercel platform limitations on model sizes
4. documentation gaps: Some edge case handling not documented

## 12. Audit Report Template
| Category          | Implemented | Simulated | Documented-Only | Config-Required |
|-------------------|-------------|-----------|------------------|------------------|
| API Routes        | ✅          | ❌        | ✅               | ✅               |
| Policy Engine      | ✅          | ❌        | ✅               | ✅               |
| Threat Detection   | ✅          | ✅        | ✅               | ✅               |
| Secret Detection   | ✅          | ❌        | ✅               | ✅               |
| Rewrite Engine     | ✅          | ❌        | ✅               | ✅               |
| Authentication     | ✅          | ❌        | ✅               | ✅               |
| Database           | ✅          | ❌        | ✅               | ✅               |
| OpenRouter         | ✅          | ❌        | ✅               | ✅               |
| Frontend Scanner   | ✅          | ❌        | ✅               | ✅               |
| Judge Mode         | ✅          | ✅        | ✅               | ✅               |

## 13. Presentation Materials
- Slide 1: Architecture Diagram
- Slide 2: Technology Stack
- Slide 3: AI Governance Pipeline
- Slide 4: Security Features
- Slide 5: Threat DetectionDemo
- Slide 6: Judge Mode Interface
- Slide 7: Deployment Diagram
- Slide 8: Limitations & Roadmap

## 14. Demo Script
1. Start with dashboard view showing normal operations
2. Demonstrate input that triggers threat detection
3. Show policy engine blocking dangerous request
4. Demonstrate secret detection in input
5. Switch to judge mode to review and override
6. Show audit trail of all actions

## 15. Q&A Preparation
Q: How does SentinelX ensure compliance with data protection regulations?
A: Through its policy engine that can be configured with jurisdiction-specific rules.

Q: What happens when the primary LLM service is unavailable?
A: The system automatically falls back to local models with graceful degradation.

Q: Can SentinelX be integrated with enterprise identity providers?
A: Yes, through NextAuth's extensible authentication providers.

Q: How are secrets handled in the system?
A: Through automatic detection, logging, and potential blocking based on configured policies.