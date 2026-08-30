export type RoleId = "super-admin" | "security-admin" | "soc-analyst" | "compliance-officer" | "engineering-manager" | "employee" | "auditor";

export interface RoleDef {
  id: RoleId;
  label: string;
  short: string;
  color: string;
  initials: string;
  persona: string;
  landing: string;
  tagline: string;
  can: string[];
  nav: string[];
}

export const ROLES: RoleDef[] = [
  {
    id: "super-admin",
    label: "Super Admin",
    short: "SUP",
    color: "text-status-critical",
    initials: "SA",
    persona: "Aarav Mehta",
    landing: "/executive",
    tagline: "Full platform control — every module, every toggle.",
    can: ["*"],
    nav: ["*"],
  },
  {
    id: "security-admin",
    label: "Security Admin",
    short: "ADM",
    color: "text-accent-light",
    initials: "AM",
    persona: "Aarav Mehta",
    landing: "/executive",
    tagline: "Configures policies, agents, and enforcement rules.",
    can: ["policy:write", "settings:write", "incident:manage", "report:read"],
    nav: ["executive", "dashboard", "soc", "scanner", "twin", "intelligence", "explain", "analytics", "copilot", "incidents", "threats", "activity", "policies", "agents", "audit", "reports", "compliance", "system", "settings"],
  },
  {
    id: "soc-analyst",
    label: "SOC Analyst",
    short: "SOC",
    color: "text-status-high",
    initials: "KS",
    persona: "Kenji Watanabe",
    landing: "/soc",
    tagline: "Triage, investigate, and resolve incidents around the clock.",
    can: ["incident:manage", "incident:comment", "scan:run"],
    nav: ["soc", "dashboard", "incidents", "scanner", "threats", "activity", "audit", "explain", "copilot", "agents"],
  },
  {
    id: "compliance-officer",
    label: "Compliance Officer",
    short: "COM",
    color: "text-status-low",
    initials: "SR",
    persona: "Sofia Reyes",
    landing: "/compliance",
    tagline: "Audits regulation coverage and compliance posture.",
    can: ["report:read", "policy:read", "incident:comment"],
    nav: ["compliance", "executive", "reports", "policies", "incidents", "analytics", "twin", "copilot", "activity"],
  },
  {
    id: "engineering-manager",
    label: "Engineering Manager",
    short: "ENG",
    color: "text-status-info",
    initials: "DO",
    persona: "Daniel Okafor",
    landing: "/twin",
    tagline: "Owns team risk, secrets hygiene, and gateway integration.",
    can: ["scan:run", "report:read", "incident:comment"],
    nav: ["twin", "executive", "incidents", "scanner", "activity", "analytics", "reports", "policies", "copilot"],
  },
  {
    id: "employee",
    label: "Employee",
    short: "EMP",
    color: "text-text-muted",
    initials: "ME",
    persona: "Meera Kapoor",
    landing: "/scanner",
    tagline: "Scans prompts before sending them to AI assistants.",
    can: ["scan:run"],
    nav: ["scanner", "copilot", "executive"],
  },
  {
    id: "auditor",
    label: "Auditor",
    short: "AUD",
    color: "text-status-medium",
    initials: "MK",
    persona: "Maya Iyer",
    landing: "/audit",
    tagline: "Read-only review of logs, reports, and compliance evidence.",
    can: ["report:read", "audit:read"],
    nav: ["audit", "reports", "compliance", "activity", "policies", "incidents"],
  },
];

export const ROLE_BY_ID = new Map(ROLES.map((r) => [r.id, r]));

export function navAllowed(role: RoleId | null, key: string): boolean {
  const def = role ? ROLE_BY_ID.get(role) : undefined;
  if (!def) return true;
  if (def.nav.includes("*")) return true;
  return def.nav.includes(key);
}

export function landingFor(role: RoleId | null): string {
  const def = role ? ROLE_BY_ID.get(role) : undefined;
  return def?.landing ?? "/executive";
}
