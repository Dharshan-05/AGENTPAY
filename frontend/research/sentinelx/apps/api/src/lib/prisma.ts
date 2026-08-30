import { PrismaClient } from '@prisma/client';
import { randomUUID } from 'node:crypto';

type PrismaLike = PrismaClient;

const globalForPrisma = globalThis as unknown as { prisma?: PrismaLike };

export const prisma: PrismaLike = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

export async function dbAvailable(): Promise<boolean> {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return true;
  } catch {
    return false;
  }
}

export function newId(): string {
  return randomUUID();
}
