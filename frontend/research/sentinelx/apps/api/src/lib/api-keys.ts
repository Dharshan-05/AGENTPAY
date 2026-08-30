import crypto from 'crypto';

/**
 * Generate a new cryptographically secure API key.
 * Format: sx_live_<48-char hex string>
 * Returns the raw secret, the prefix for UI display, and the SHA-256 hash for database storage.
 */
export function generateApiKey(name: string) {
  // Generate 24 bytes (48 hex chars)
  const randomBytes = crypto.randomBytes(24).toString('hex');
  const rawSecret = `sx_live_${randomBytes}`;
  
  // Prefix for display (e.g. sx_live_ab12)
  const keyPrefix = rawSecret.slice(0, 12);
  
  // SHA-256 Hash for storage
  const keyHash = crypto.createHash('sha256').update(rawSecret).digest('hex');

  return {
    rawSecret,
    keyPrefix,
    keyHash,
    name
  };
}

/**
 * Hash an incoming API key to lookup in the database.
 */
export function hashIncomingKey(rawSecret: string): string {
  return crypto.createHash('sha256').update(rawSecret).digest('hex');
}
