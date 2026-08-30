import { prisma, dbAvailable } from './prisma';

type Json = unknown;

interface MemModels {
  auditLog: any[];
  user: any[];
  policy: any[];
  detectionRule: any[];
  alert: any[];
  setting: any[];
  session: any[];
  riskEvent: any[];
  apiKey: any[];
  organization: any[];
  aiRequest: any[];
  usageLedger: any[];
  budget: any[];
  quota: any[];
  rateLimitPolicy: any[];
  employeeModelPermission: any[];
  employeeProviderPermission: any[];
}

interface MemRecord {
  id: string;
  [key: string]: unknown;
  createdAt?: Date;
  timestamp?: Date;
  user?: MemRecord | null;
}

const mem: MemModels = {
  auditLog: [],
  user: [],
  policy: [],
  detectionRule: [],
  alert: [],
  setting: [],
  session: [],
  riskEvent: [],
  apiKey: [],
  organization: [],
  aiRequest: [],
  usageLedger: [],
  budget: [],
  quota: [],
  rateLimitPolicy: [],
  employeeModelPermission: [],
  employeeProviderPermission: [],
};

let useMem = false;
let checked = false;

async function init(): Promise<void> {
  if (checked) return;
  checked = true;
  try {
    useMem = !(await dbAvailable());
  } catch {
    useMem = true;
  }
  if (useMem) console.log('[store] PostgreSQL unavailable — running in in-memory demo mode');
}

function newId(): string {
  return globalThis.crypto?.randomUUID?.() ?? `id-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function today(): Date {
  return new Date();
}

function matchesWhere(rec: any, where?: Record<string, unknown>): boolean {
  if (!where) return true;
  for (const [key, value] of Object.entries(where)) {
    if (key === 'OR' && Array.isArray(value)) {
      if (!(value as any[]).some((sub) => matchesWhere(rec, sub))) return false;
      continue;
    }
    if (key === 'AND' && Array.isArray(value)) {
      if (!(value as any[]).every((sub) => matchesWhere(rec, sub))) return false;
      continue;
    }
    if (key === 'decision' && typeof value === 'object' && value !== null && 'in' in (value as any)) {
      if (!(value as any).in.includes(rec.decision)) return false;
      continue;
    }
    if (key === 'timestamp' || key === 'createdAt') {
      const gte = (value as any)?.gte;
      if (gte && new Date(rec[key]).getTime() < new Date(gte).getTime()) return false;
      continue;
    }
    if (key === 'riskScore') {
      const gte = (value as any)?.gte;
      if (gte && Number(rec.riskScore) < gte) return false;
      continue;
    }
    if (key === 'decision' && Array.isArray(value)) {
      if (!value.includes(rec.decision)) return false;
      continue;
    }
    if (key === 'active') {
      if (rec.active !== value) return false;
      continue;
    }
    if (key === 'enabled' && value === undefined) continue;
    if (rec[key] === undefined || rec[key] === null) return false;
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      if (key === 'contains') continue;
      const contains = (value as any)?.contains;
      if (contains !== undefined) {
        const target = String(rec[key] ?? '');
        if (!target.toLowerCase().includes(String(contains).toLowerCase())) return false;
        continue;
      }
      if (rec[key] !== value) return false;
    } else if (rec[key] !== value) return false;
  }
  return true;
}

function memFindAll(model: keyof MemModels, where?: any): MemRecord[] {
  const rows = mem[model] as MemRecord[];
  return rows.filter((r) => matchesWhere(r, where));
}

export const store = {
  async useMemory(): Promise<boolean> {
    await init();
    return useMem;
  },

  auditLog: {
    async create(data: any) {
      await init();
      if (!useMem) return prisma.auditLog.create({ data, include: { user: true } });
      const payload = data.data ?? data;
      const rec: MemRecord = { id: newId(), createdAt: today(), timestamp: today(), ...payload };
      rec.user = rec.userId ? mem.user.find((u) => u.id === rec.userId) ?? null : null;
      mem.auditLog.unshift(rec);
      return rec;
    },
    async count(where?: any) {
      await init();
      const w = where?.where ?? where;
      if (!useMem) return prisma.auditLog.count({ where: w });
      return memFindAll('auditLog', w).length;
    },
    async findMany(args?: any) {
      await init();
      if (!useMem) {
        const { where, orderBy, skip, take, include } = args ?? {};
        return prisma.auditLog.findMany({
          where,
          orderBy: orderBy ?? { timestamp: 'desc' },
          skip,
          take,
          include,
        });
      }
  let rows = memFindAll('auditLog', args?.where);
  if (args?.orderBy?.timestamp === 'desc') {
    rows = rows.sort((a, b) => new Date(String(b.timestamp ?? 0)).getTime() - new Date(String(a.timestamp ?? 0)).getTime());
  } else if (args?.orderBy?.riskScore === 'desc') {
    rows = rows.sort((a, b) => Number(b.riskScore) - Number(a.riskScore));
  }
      if (args?.take) rows = rows.slice(args.skip ?? 0, (args.skip ?? 0) + args.take);
      return rows.map((r) => ({ ...r, user: r.userId ? mem.user.find((u) => u.id === r.userId) ?? null : null }));
    },
    async findUnique(args: { where: { id: string }; include?: any }) {
      await init();
      if (!useMem) return prisma.auditLog.findUnique(args);
      const rec = mem.auditLog.find((r) => r.id === args.where.id);
      return rec ? { ...rec, user: rec.userId ? mem.user.find((u) => u.id === rec.userId) ?? null : null } : null;
    },
  },

  user: {
    async upsert(args: any) {
      await init();
      if (!useMem) return prisma.user.upsert(args);
      const existing = mem.user.find((u) => u.email === args.where.email);
      if (existing) {
        Object.assign(existing, args.update);
        return existing;
      }
      const rec: MemRecord = { id: newId(), createdAt: today(), ...(args.create ?? args) };
      mem.user.push(rec);
      return rec;
    },
    async findMany(args?: any) {
      await init();
      if (!useMem) return prisma.user.findMany(args);
      let rows = memFindAll('user', args?.where);
      return rows.map(({ password, ...rest }) => rest);
    },
    async findFirst(args: any) {
      await init();
      if (!useMem) return prisma.user.findFirst(args);
      const rows = memFindAll('user', args?.where);
      return rows.length > 0 ? rows[0] : null;
    },
    async count(where?: any) {
      await init();
      if (!useMem) return prisma.user.count(where);
      return memFindAll('user', where).length;
    },
    async create(args: any) {
      await init();
      if (!useMem) return prisma.user.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), ...args };
      mem.user.push(rec);
      return rec;
    },
    async update(args: any) {
      await init();
      if (!useMem) return prisma.user.update(args);
      const existing = mem.user.find((u) => u.id === args.where.id);
      if (existing) {
        Object.assign(existing, args.data);
        return existing;
      }
      return null;
    },
    async findUnique(args: { where: { id?: string }; include?: any }) {
      await init();
      if (!useMem) return prisma.user.findUnique(args as any);
      const rec = mem.user.find((r) => r.id === args.where.id);
      return rec ? { ...rec, password: undefined } : null;
    },
  },

  policy: {
    async count() {
      await init();
      if (!useMem) return prisma.policy.count();
      return mem.policy.length;
    },
    async findMany() {
      await init();
      if (!useMem) return prisma.policy.findMany({ orderBy: { createdAt: 'asc' } });
      return mem.policy;
    },
    async createMany(args: any) {
      await init();
      if (!useMem) return prisma.policy.createMany(args);
      for (const d of args.data) mem.policy.push({ id: newId(), createdAt: today(), updatedAt: today(), ...d });
      return { count: args.data.length };
    },
  },

  detectionRule: {
    async count() {
      await init();
      if (!useMem) return prisma.detectionRule.count();
      return mem.detectionRule.length;
    },
    async findMany() {
      await init();
      if (!useMem) return prisma.detectionRule.findMany({ orderBy: { category: 'asc' } });
      return mem.detectionRule;
    },
    async createMany(args: any) {
      await init();
      if (!useMem) return prisma.detectionRule.createMany(args);
      for (const d of args.data) mem.detectionRule.push({ id: newId(), createdAt: today(), ...d });
      return { count: args.data.length };
    },
  },

  alert: {
    async count() {
      await init();
      if (!useMem) return prisma.alert.count();
      return mem.alert.length;
    },
    async findMany(args?: any) {
      await init();
      if (!useMem) return prisma.alert.findMany({ orderBy: { createdAt: 'desc' }, take: args?.take });
      let rows = [...mem.alert].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
      if (args?.take) rows = rows.slice(0, args.take);
      return rows;
    },
    async createMany(args: any) {
      await init();
      if (!useMem) return prisma.alert.createMany(args);
      for (const d of args.data) mem.alert.push({ id: newId(), createdAt: today(), ...d });
      return { count: args.data.length };
    },
    async update(args: any) {
      await init();
      if (!useMem) return prisma.alert.update(args);
      const rec = mem.alert.find((a) => a.id === args.where.id);
      if (rec) Object.assign(rec, args.data);
      return rec;
    },
  },

  setting: {
    async count() {
      await init();
      if (!useMem) return prisma.setting.count();
      return mem.setting.length;
    },
    async findMany() {
      await init();
      if (!useMem) return prisma.setting.findMany();
      return mem.setting;
    },
    async createMany(args: any) {
      await init();
      if (!useMem) return prisma.setting.createMany(args);
      for (const d of args.data) mem.setting.push({ id: newId(), updatedAt: today(), ...d });
      return { count: args.data.length };
    },
  },

  session: {
    async count(where?: any) {
      await init();
      if (!useMem) return prisma.session.count({ where });
      return mem.session.filter((s) => s.active === true).length;
    },
  },

  riskEvent: {
    async create(data: any) {
      await init();
      if (!useMem) return prisma.riskEvent.create({ data });
      const rec: MemRecord = { id: newId(), createdAt: today(), ...data };
      mem.riskEvent.push(rec);
      return rec;
    },
  },

  apiKey: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.apiKey.create(args);
      const rec: MemRecord = {
        id: newId(),
        createdAt: today(),
        updatedAt: today(),
        lastUsedAt: null,
        expiresAt: null,
        revokedAt: null,
        ...(args.data ?? args),
      };
      mem.apiKey.push(rec);
      return rec;
    },
    async findFirst(args: any) {
      await init();
      if (!useMem) return prisma.apiKey.findFirst(args);
      const rows = memFindAll('apiKey', args?.where);
      return rows.length > 0 ? rows[0] : null;
    },
    async findUnique(args: { where: { id: string } }) {
      await init();
      if (!useMem) return prisma.apiKey.findUnique(args);
      return mem.apiKey.find((k) => k.id === args.where.id) ?? null;
    },
    async findMany(args?: any) {
      await init();
      if (!useMem) {
        const { where, select, orderBy } = args ?? {};
        return prisma.apiKey.findMany({ where, select, orderBy });
      }
      let rows = memFindAll('apiKey', args?.where);
      if (args?.orderBy?.createdAt === 'desc') {
        rows = rows.sort((a, b) => new Date(String(b.createdAt)).getTime() - new Date(String(a.createdAt)).getTime());
      }
      if (args?.select) {
        rows = rows.map((r) => {
          const out: any = {};
          for (const k of Object.keys(args.select)) out[k] = r[k];
          return out;
        });
      }
      return rows;
    },
    async update(args: any) {
      await init();
      if (!useMem) return prisma.apiKey.update(args);
      const rec = mem.apiKey.find((k) => k.id === args.where.id);
      if (rec) Object.assign(rec, { ...args.data, updatedAt: today() });
      return rec ?? null;
    },
  },

  organization: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.organization.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), updatedAt: today(), ...(args.data ?? args) };
      mem.organization.push(rec);
      return rec;
    },
    async findFirst(args: any) {
      await init();
      if (!useMem) return prisma.organization.findFirst(args);
      const rows = memFindAll('organization', args?.where);
      return rows.length > 0 ? rows[0] : null;
    },
    async findUnique(args: { where: { id: string } }) {
      await init();
      if (!useMem) return prisma.organization.findUnique(args);
      return mem.organization.find((o) => o.id === args.where.id) ?? null;
    },
  },

  aiRequest: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.aIRequest.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), ...(args.data ?? args) };
      mem.aiRequest.push(rec);
      return rec;
    },
    async findMany(args?: any) {
      await init();
      if (!useMem) return prisma.aIRequest.findMany(args ?? {});
      let rows = memFindAll('aiRequest', args?.where);
      if (args?.take) rows = rows.slice(0, args.take);
      return rows;
    },
  },

  usageLedger: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.usageLedger.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), ...(args.data ?? args) };
      mem.usageLedger.push(rec);
      return rec;
    },
    async findMany(args?: any) {
      await init();
      if (!useMem) return prisma.usageLedger.findMany(args ?? {});
      let rows = memFindAll('usageLedger', args?.where);
      if (args?.orderBy?.createdAt === 'desc') {
        rows = rows.sort((a, b) => new Date(String(b.createdAt)).getTime() - new Date(String(a.createdAt)).getTime());
      }
      if (args?.take) rows = rows.slice(0, args.take);
      return rows;
    },
    async aggregate(args?: any) {
      await init();
      if (!useMem) return (prisma.usageLedger as any).aggregate(args ?? {});
      const rows = memFindAll('usageLedger', args?.where);
      return {
        _sum: {
          inputTokens:   rows.reduce((s: number, r: any) => s + (r.inputTokens ?? 0), 0),
          outputTokens:  rows.reduce((s: number, r: any) => s + (r.outputTokens ?? 0), 0),
          totalTokens:   rows.reduce((s: number, r: any) => s + (r.totalTokens ?? 0), 0),
          estimatedCost: rows.reduce((s: number, r: any) => s + (r.estimatedCost ?? 0), 0),
        },
        _count: { id: rows.length },
      };
    },
  },

  employeeModelPermission: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.employeeModelPermission.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), updatedAt: today(), ...(args.data ?? args) };
      mem.employeeModelPermission.push(rec);
      return rec;
    },
    async findFirst(args: any) {
      await init();
      if (!useMem) return prisma.employeeModelPermission.findFirst(args);
      const rows = memFindAll('employeeModelPermission', args?.where);
      return rows.length > 0 ? rows[0] : null;
    }
  },

  employeeProviderPermission: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.employeeProviderPermission.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), updatedAt: today(), ...(args.data ?? args) };
      mem.employeeProviderPermission.push(rec);
      return rec;
    },
    async findFirst(args: any) {
      await init();
      if (!useMem) return prisma.employeeProviderPermission.findFirst(args);
      const rows = memFindAll('employeeProviderPermission', args?.where);
      return rows.length > 0 ? rows[0] : null;
    }
  },

  quota: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.quota.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), updatedAt: today(), ...(args.data ?? args) };
      mem.quota.push(rec);
      return rec;
    },
    async findFirst(args: any) {
      await init();
      if (!useMem) return prisma.quota.findFirst(args);
      const rows = memFindAll('quota', args?.where);
      return rows.length > 0 ? rows[0] : null;
    }
  },

  budget: {
    async create(args: any) {
      await init();
      if (!useMem) return prisma.budget.create(args);
      const rec: MemRecord = { id: newId(), createdAt: today(), updatedAt: today(), ...(args.data ?? args) };
      mem.budget.push(rec);
      return rec;
    },
    async findFirst(args: any) {
      await init();
      if (!useMem) return prisma.budget.findFirst(args);
      const rows = memFindAll('budget', args?.where);
      return rows.length > 0 ? rows[0] : null;
    }
  }
};

export type Store = typeof store;
export type Json2 = Json;
