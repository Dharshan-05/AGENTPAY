# AGENTPAY — 11: Centralized Configuration System (`@agentpay/config`)

## 1. Typed Configuration Architecture

Environment variables are loaded and validated at process startup using `@agentpay/config`:

```typescript
import { z } from 'zod';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'staging', 'production']).default('development'),
  PORT: z.coerce.number().default(4000),
  DATABASE_URL: z.string().url(),
  REDIS_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  RAZORPAY_KEY_ID: z.string().startsWith('rzp_test_'),
  RAZORPAY_KEY_SECRET: z.string().min(16),
  RAZORPAY_WEBHOOK_SECRET: z.string().min(16)
});

export type EnvConfig = z.infer<typeof envSchema>;
```

If validation fails, the service aborts immediately with a clear diagnostic log.
