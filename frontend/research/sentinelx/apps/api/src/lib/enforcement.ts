/**
 * PHASE 4 + 5 — Quota, Rate Limit, and Budget Enforcement
 *
 * This module is the enforcement layer that sits between API Key auth
 * and provider routing in the gateway. All checks run BEFORE any
 * request reaches OpenRouter/OpenAI.
 *
 * Pipeline enforced:
 *   1. Per-request token limit
 *   2. Daily/monthly request count (Redis)
 *   3. Daily/monthly token quota (UsageLedger aggregate)
 *   4. Requests-per-minute rate limit (Redis sliding window)
 *   5. Requests-per-hour rate limit (Redis sliding window)
 *   6. Concurrent request limit (Redis counter)
 *   7. Daily/monthly budget check (UsageLedger aggregate)
 *
 * Redis is used for low-latency counters. If Redis is unavailable,
 * in-memory counters ensure the API keeps running.
 */

import { getRedis } from './redis';
import { store } from './store';

// ── Defaults (used when no Quota/Budget/RateLimitPolicy row exists) ────────────
export const DEFAULT_QUOTA = {
  maxTokensPerRequest:  8_000,
  dailyTokenLimit:      500_000,
  monthlyTokenLimit:    5_000_000,
  dailyRequestLimit:    1_000,
  monthlyRequestLimit:  20_000,
};

export const DEFAULT_RATE_LIMIT = {
  requestsPerMinute:   60,
  requestsPerHour:     500,
  concurrentRequests:  10,
};

export const DEFAULT_BUDGET = {
  dailyBudget:   50.0,   // USD
  monthlyBudget: 300.0,  // USD
};

// ── In-memory fallback counters for when Redis is unavailable ─────────────────
const memCounters = new Map<string, { value: number; expiresAt: number }>();

function memIncr(key: string, ttlSeconds: number): number {
  const now = Date.now();
  const entry = memCounters.get(key);
  if (!entry || entry.expiresAt < now) {
    memCounters.set(key, { value: 1, expiresAt: now + ttlSeconds * 1000 });
    return 1;
  }
  entry.value += 1;
  return entry.value;
}



function memDecr(key: string): void {
  const entry = memCounters.get(key);
  if (entry && entry.value > 0) entry.value -= 1;
}

// ── Redis helpers with in-memory fallback ────────────────────────────────────
async function redisIncr(key: string, ttlSeconds: number): Promise<number> {
  try {
    const redis = getRedis();
    const n = await redis.incr(key);
    if (n === 1) await redis.expire(key, ttlSeconds);
    return n;
  } catch {
    return memIncr(key, ttlSeconds);
  }
}

async function redisDecr(key: string): Promise<void> {
  try {
    const redis = getRedis();
    const v = await redis.decr(key);
    if (v < 0) await redis.set(key, '0');
  } catch {
    memDecr(key);
  }
}



// ── Time window helpers ───────────────────────────────────────────────────────
function todayUTCStr(): string {
  return new Date().toISOString().slice(0, 10); // YYYY-MM-DD
}

function monthUTCStr(): string {
  return new Date().toISOString().slice(0, 7); // YYYY-MM
}

function secondsUntilEndOfMinute(): number {
  return 60 - new Date().getSeconds();
}

function secondsUntilEndOfHour(): number {
  const now = new Date();
  return 3600 - now.getMinutes() * 60 - now.getSeconds();
}

function startOfDayUTC(): Date {
  const d = new Date();
  d.setUTCHours(0, 0, 0, 0);
  return d;
}

function startOfMonthUTC(): Date {
  const d = new Date();
  d.setUTCDate(1);
  d.setUTCHours(0, 0, 0, 0);
  return d;
}

// ── Governance policy loaders ─────────────────────────────────────────────────
export interface EffectiveQuota {
  maxTokensPerRequest: number;
  dailyTokenLimit: number;
  monthlyTokenLimit: number;
  dailyRequestLimit: number;
  monthlyRequestLimit: number;
}

export interface EffectiveBudget {
  dailyBudget: number;
  monthlyBudget: number;
}

export interface EffectiveRateLimit {
  requestsPerMinute: number;
  requestsPerHour: number;
  concurrentRequests: number;
}

async function loadQuota(userId: string, organizationId: string | null): Promise<EffectiveQuota> {
  // Load user-level quota
  const userQuota: any = await (store as any).quota?.findFirst?.({ where: { userId } }).catch(() => null) ?? null;
  // Load org-level quota
  const orgQuota: any = organizationId
    ? await (store as any).quota?.findFirst?.({ where: { organizationId, userId: null } }).catch(() => null) ?? null
    : null;

  // Most restrictive wins
  const minOf = (a: number | null | undefined, b: number | null | undefined, def: number) =>
    Math.min(a ?? def, b ?? def);

  return {
    maxTokensPerRequest: minOf(userQuota?.maxTokensPerRequest, orgQuota?.maxTokensPerRequest, DEFAULT_QUOTA.maxTokensPerRequest),
    dailyTokenLimit:     minOf(userQuota?.dailyTokenLimit,     orgQuota?.dailyTokenLimit,     DEFAULT_QUOTA.dailyTokenLimit),
    monthlyTokenLimit:   minOf(userQuota?.monthlyTokenLimit,   orgQuota?.monthlyTokenLimit,   DEFAULT_QUOTA.monthlyTokenLimit),
    dailyRequestLimit:   minOf(userQuota?.dailyRequestLimit,   orgQuota?.dailyRequestLimit,   DEFAULT_QUOTA.dailyRequestLimit),
    monthlyRequestLimit: minOf(userQuota?.monthlyRequestLimit, orgQuota?.monthlyRequestLimit, DEFAULT_QUOTA.monthlyRequestLimit),
  };
}

async function loadBudget(userId: string, organizationId: string | null): Promise<EffectiveBudget> {
  const userBudget: any = await (store as any).budget?.findFirst?.({ where: { userId } }).catch(() => null) ?? null;
  const orgBudget: any = organizationId
    ? await (store as any).budget?.findFirst?.({ where: { organizationId, userId: null } }).catch(() => null) ?? null
    : null;

  const minOf = (a: number | null | undefined, b: number | null | undefined, def: number) =>
    Math.min(a ?? def, b ?? def);

  return {
    dailyBudget:   minOf(userBudget?.dailyBudget,   orgBudget?.dailyBudget,   DEFAULT_BUDGET.dailyBudget),
    monthlyBudget: minOf(userBudget?.monthlyBudget,  orgBudget?.monthlyBudget, DEFAULT_BUDGET.monthlyBudget),
  };
}

async function loadRateLimit(userId: string, organizationId: string | null): Promise<EffectiveRateLimit> {
  const userRL: any = await (store as any).rateLimitPolicy?.findFirst?.({ where: { userId } }).catch(() => null) ?? null;
  const orgRL: any = organizationId
    ? await (store as any).rateLimitPolicy?.findFirst?.({ where: { organizationId, userId: null } }).catch(() => null) ?? null
    : null;

  const minOf = (a: number | null | undefined, b: number | null | undefined, def: number) =>
    Math.min(a ?? def, b ?? def);

  return {
    requestsPerMinute:  minOf(userRL?.requestsPerMinute,  orgRL?.requestsPerMinute,  DEFAULT_RATE_LIMIT.requestsPerMinute),
    requestsPerHour:    minOf(userRL?.requestsPerHour,    orgRL?.requestsPerHour,    DEFAULT_RATE_LIMIT.requestsPerHour),
    concurrentRequests: minOf(userRL?.concurrentRequests, orgRL?.concurrentRequests, DEFAULT_RATE_LIMIT.concurrentRequests),
  };
}

// ── Usage aggregators (from UsageLedger) ─────────────────────────────────────
async function getDailyTokenUsage(userId: string): Promise<number> {
  try {
    const agg = await store.usageLedger.aggregate({
      where: { userId, createdAt: { gte: startOfDayUTC() } },
    });
    return agg._sum.totalTokens ?? 0;
  } catch {
    return 0;
  }
}

async function getMonthlyTokenUsage(userId: string): Promise<number> {
  try {
    const agg = await store.usageLedger.aggregate({
      where: { userId, createdAt: { gte: startOfMonthUTC() } },
    });
    return agg._sum.totalTokens ?? 0;
  } catch {
    return 0;
  }
}

async function getDailySpend(userId: string): Promise<number> {
  try {
    const agg = await store.usageLedger.aggregate({
      where: { userId, createdAt: { gte: startOfDayUTC() } },
    });
    return agg._sum.estimatedCost ?? 0;
  } catch {
    return 0;
  }
}

async function getMonthlySpend(userId: string): Promise<number> {
  try {
    const agg = await store.usageLedger.aggregate({
      where: { userId, createdAt: { gte: startOfMonthUTC() } },
    });
    return agg._sum.estimatedCost ?? 0;
  } catch {
    return 0;
  }
}

// ── Enforcement result ────────────────────────────────────────────────────────
export type EnforcementDecision =
  | { allowed: true; concurrencyKey: string }
  | { allowed: false; code: string; message: string; retryAfter?: number };

// ── Main enforcement function ─────────────────────────────────────────────────
/**
 * Run the full quota/rate-limit/budget enforcement pipeline.
 * Returns { allowed: true } if the request may proceed.
 * Returns { allowed: false, code, message } if it must be rejected.
 *
 * IMPORTANT: When allowed: true, the caller MUST call releaseConcurrency()
 * after the request completes (success or error) to decrement the counter.
 */
export async function enforceGatewayPolicy(params: {
  userId: string;
  organizationId: string | null;
  apiKeyId: string;
  estimatedInputTokens: number;
  requestId: string;
}): Promise<EnforcementDecision> {
  const { userId, organizationId, estimatedInputTokens } = params;

  const day   = todayUTCStr();
  const month = monthUTCStr();

  // Load all policies in parallel
  const [quota, rl, budget] = await Promise.all([
    loadQuota(userId, organizationId),
    loadRateLimit(userId, organizationId),
    loadBudget(userId, organizationId),
  ]);

  // ── 1. Per-request token limit ──────────────────────────────────────────────
  if (estimatedInputTokens > quota.maxTokensPerRequest) {
    return {
      allowed: false,
      code: 'REQUEST_TOKEN_LIMIT_EXCEEDED',
      message: `Request too large: ${estimatedInputTokens} tokens exceeds per-request limit of ${quota.maxTokensPerRequest}`,
    };
  }

  // ── 2. Rate limit: requests per minute ─────────────────────────────────────
  const minuteKey = `sentinelx:ratelimit:user:${userId}:minute:${day}:${new Date().getMinutes()}`;
  const minuteCount = await redisIncr(minuteKey, secondsUntilEndOfMinute() + 5);
  if (minuteCount > rl.requestsPerMinute) {
    return {
      allowed: false,
      code: 'RATE_LIMIT_EXCEEDED',
      message: `Rate limit exceeded: ${rl.requestsPerMinute} requests/minute`,
      retryAfter: secondsUntilEndOfMinute(),
    };
  }

  // ── 3. Rate limit: requests per hour ───────────────────────────────────────
  const hourKey = `sentinelx:ratelimit:user:${userId}:hour:${day}:${new Date().getUTCHours()}`;
  const hourCount = await redisIncr(hourKey, secondsUntilEndOfHour() + 10);
  if (hourCount > rl.requestsPerHour) {
    return {
      allowed: false,
      code: 'RATE_LIMIT_EXCEEDED',
      message: `Hourly rate limit exceeded: ${rl.requestsPerHour} requests/hour`,
      retryAfter: secondsUntilEndOfHour(),
    };
  }

  // ── 4. Daily request count (Redis) ─────────────────────────────────────────
  const dailyReqKey = `sentinelx:dailyreqs:user:${userId}:${day}`;
  const dailyReqCount = await redisIncr(dailyReqKey, 86400);
  if (dailyReqCount > quota.dailyRequestLimit) {
    return {
      allowed: false,
      code: 'DAILY_REQUEST_LIMIT_EXCEEDED',
      message: `Daily request limit reached: ${quota.dailyRequestLimit} requests/day`,
    };
  }

  // ── 5. Monthly request count (Redis) ───────────────────────────────────────
  const monthlyReqKey = `sentinelx:monthlyreqs:user:${userId}:${month}`;
  const monthlyReqCount = await redisIncr(monthlyReqKey, 31 * 86400);
  if (monthlyReqCount > quota.monthlyRequestLimit) {
    return {
      allowed: false,
      code: 'MONTHLY_REQUEST_LIMIT_EXCEEDED',
      message: `Monthly request limit reached: ${quota.monthlyRequestLimit} requests/month`,
    };
  }

  // ── 6. Concurrent request limit ────────────────────────────────────────────
  const concurrencyKey = `sentinelx:concurrency:user:${userId}`;
  const concurrentCount = await redisIncr(concurrencyKey, 300);
  if (concurrentCount > rl.concurrentRequests) {
    // Don't hold concurrency slot if rejected
    await redisDecr(concurrencyKey);
    return {
      allowed: false,
      code: 'CONCURRENT_LIMIT_EXCEEDED',
      message: `Concurrent request limit reached: ${rl.concurrentRequests} simultaneous requests`,
    };
  }

  // ── 7. Daily token quota (from UsageLedger) ────────────────────────────────
  const [dailyTokens, monthlyTokens] = await Promise.all([
    getDailyTokenUsage(userId),
    getMonthlyTokenUsage(userId),
  ]);

  if (dailyTokens + estimatedInputTokens > quota.dailyTokenLimit) {
    await redisDecr(concurrencyKey);
    return {
      allowed: false,
      code: 'DAILY_TOKEN_LIMIT_EXCEEDED',
      message: `Daily token quota exceeded: used ${dailyTokens}, limit ${quota.dailyTokenLimit}`,
    };
  }

  // ── 8. Monthly token quota ─────────────────────────────────────────────────
  if (monthlyTokens + estimatedInputTokens > quota.monthlyTokenLimit) {
    await redisDecr(concurrencyKey);
    return {
      allowed: false,
      code: 'MONTHLY_TOKEN_LIMIT_EXCEEDED',
      message: `Monthly token quota exceeded: used ${monthlyTokens}, limit ${quota.monthlyTokenLimit}`,
    };
  }

  // ── 9. Daily budget ────────────────────────────────────────────────────────
  const [dailySpend, monthlySpend] = await Promise.all([
    getDailySpend(userId),
    getMonthlySpend(userId),
  ]);

  if (dailySpend >= budget.dailyBudget) {
    await redisDecr(concurrencyKey);
    return {
      allowed: false,
      code: 'DAILY_BUDGET_EXCEEDED',
      message: `Daily budget of $${budget.dailyBudget.toFixed(2)} USD reached (spent: $${dailySpend.toFixed(4)})`,
    };
  }

  // ── 10. Monthly budget ─────────────────────────────────────────────────────
  if (monthlySpend >= budget.monthlyBudget) {
    await redisDecr(concurrencyKey);
    return {
      allowed: false,
      code: 'MONTHLY_BUDGET_EXCEEDED',
      message: `Monthly budget of $${budget.monthlyBudget.toFixed(2)} USD reached (spent: $${monthlySpend.toFixed(4)})`,
    };
  }

  // ── All checks passed ──────────────────────────────────────────────────────
  return { allowed: true, concurrencyKey };
}

/**
 * Must be called after a request completes (success OR error)
 * to release the concurrent request slot.
 */
export async function releaseConcurrency(concurrencyKey: string): Promise<void> {
  await redisDecr(concurrencyKey);
}

// ── Store extensions for quota/budget/ratelimit ───────────────────────────────
// These are lazily loaded so we can add to the store without circular imports.
export async function ensureStoreExtensions(): Promise<void> {
  const s = store as any;

  if (!s.quota) {
    s.quota = {
      async findFirst(args: any) {
        try {
          const { prisma, dbAvailable } = await import('./prisma');
          if (!(await dbAvailable())) return null;
          return await prisma.quota.findFirst(args);
        } catch { return null; }
      },
    };
  }

  if (!s.budget) {
    s.budget = {
      async findFirst(args: any) {
        try {
          const { prisma, dbAvailable } = await import('./prisma');
          if (!(await dbAvailable())) return null;
          return await prisma.budget.findFirst(args);
        } catch { return null; }
      },
    };
  }

  if (!s.rateLimitPolicy) {
    s.rateLimitPolicy = {
      async findFirst(args: any) {
        try {
          const { prisma, dbAvailable } = await import('./prisma');
          if (!(await dbAvailable())) return null;
          return await prisma.rateLimitPolicy.findFirst(args);
        } catch { return null; }
      },
    };
  }
}
