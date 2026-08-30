import Redis from 'ioredis';

let client: Redis | null = null;

export function getRedis(): Redis {
  if (!client) {
    client = new Redis(process.env.REDIS_URL || 'redis://localhost:6379', {
      lazyConnect: true,
      maxRetriesPerRequest: 1,
      retryStrategy: (times) => (times > 3 ? null : Math.min(times * 200, 1000)),
    });
    client.on('error', () => undefined);
  }
  return client;
}

export async function cacheGet<T>(key: string): Promise<T | null> {
  try {
    const value = await getRedis().get(key);
    return value ? (JSON.parse(value) as T) : null;
  } catch {
    return null;
  }
}

export async function cacheSet(key: string, value: unknown, ttlSeconds = 300): Promise<void> {
  try {
    await getRedis().set(key, JSON.stringify(value), 'EX', ttlSeconds);
  } catch {
    undefined;
  }
}

export async function cacheIncr(key: string, ttlSeconds = 3600): Promise<number> {
  try {
    const n = await getRedis().incr(key);
    if (n === 1) await getRedis().expire(key, ttlSeconds);
    return n;
  } catch {
    return 0;
  }
}

export async function seedDemoDataIfEmpty(): Promise<void> {
  const { store } = await import('./store');
  const count = await store.detectionRule.count();
  if (count > 0) return;
  const { runSeed } = await import('../seed/run');
  await runSeed();
}
