import crypto from 'crypto';

export function hashSHA256(data: string): string {
  return crypto.createHash('sha256').update(data).digest('hex');
}
