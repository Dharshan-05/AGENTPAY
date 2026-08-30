import {
  UserProfile,
  ActiveSessionRecord,
  OrganizationMemberRecord,
  RoleRecord,
  PermissionRecord,
  EnvironmentRecord,
  AuditLogRecord,
} from './source-types';

export const MOCK_PROFILE: UserProfile = {
  fullName: 'Security Administrator',
  email: 'admin@agentpay.io',
  role: 'SUPER_ADMIN',
  timezone: 'UTC (Coordinated Universal Time)',
  language: 'English (US)',
  theme: 'Dark Obsidian System',
};

export const MOCK_SESSIONS: ActiveSessionRecord[] = [
  {
    id: 'sess_1',
    device: 'Windows Workstation',
    browser: 'Chrome 128.0 (Windows 11)',
    location: 'Frankfurt, Germany',
    ipAddress: '103.14.88.19',
    lastActive: 'Just now',
    status: 'CURRENT',
  },
  {
    id: 'sess_2',
    device: 'MacBook Pro 16"',
    browser: 'Safari 17.4 (macOS Sonoma)',
    location: 'Austin, TX, US',
    ipAddress: '198.51.100.42',
    lastActive: '2 hours ago',
    status: 'ACTIVE',
  },
];

export const MOCK_MEMBERS: OrganizationMemberRecord[] = [
  { id: 'usr_1', name: 'Security Administrator', email: 'admin@agentpay.io', role: 'SUPER ADMIN', status: 'ACTIVE', lastActive: 'Just now' },
  { id: 'usr_2', name: 'Platform Lead', email: 'lead@agentpay.io', role: 'SECURITY OPERATOR', status: 'ACTIVE', lastActive: '12 mins ago' },
  { id: 'usr_3', name: 'Fraud Intelligence Analyst', email: 'fraud@agentpay.io', role: 'ANALYST', status: 'ACTIVE', lastActive: '1 hour ago' },
  { id: 'usr_4', name: 'Developer Integrator', email: 'dev@agentpay.io', role: 'DEVELOPER', status: 'INVITED', lastActive: 'Never' },
];

export const MOCK_ROLES: RoleRecord[] = [
  { id: 'rol_1', name: 'SUPER ADMIN', membersCount: 2, permissionsCount: 42, status: 'SYSTEM', description: 'Full unconstrained platform and security control' },
  { id: 'rol_2', name: 'SECURITY OPERATOR', membersCount: 5, permissionsCount: 28, status: 'SYSTEM', description: 'AgentGuard, FraudGuard, and risk policy access' },
  { id: 'rol_3', name: 'DEVELOPER', membersCount: 14, permissionsCount: 18, status: 'SYSTEM', description: 'API credentials, webhooks, and SDK playground' },
  { id: 'rol_4', name: 'ANALYST', membersCount: 8, permissionsCount: 12, status: 'CUSTOM', description: 'Analytics and financial telemetry read access' },
];

export const MOCK_PERMISSIONS: PermissionRecord[] = [
  { resource: 'PAYMENTS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'WRITE', analyst: 'READ', viewer: 'READ' },
  { resource: 'AGENTS', superAdmin: 'FULL', securityOperator: 'MANAGE', developer: 'READ', analyst: 'READ', viewer: 'READ' },
  { resource: 'AGENTGUARD', superAdmin: 'FULL', securityOperator: 'MANAGE', developer: 'EVALUATE', analyst: 'READ', viewer: 'READ' },
  { resource: 'FRAUDGUARD', superAdmin: 'FULL', securityOperator: 'MANAGE', developer: 'READ', analyst: 'READ', viewer: 'READ' },
  { resource: 'ANALYTICS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'READ', analyst: 'FULL', viewer: 'READ' },
  { resource: 'DEVELOPERS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'FULL', analyst: 'NONE', viewer: 'NONE' },
  { resource: 'SETTINGS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'NONE', analyst: 'NONE', viewer: 'NONE' },
];

export const MOCK_ENVIRONMENTS: EnvironmentRecord[] = [
  { id: 'env_prod', name: 'PRODUCTION', status: 'ACTIVE', capabilities: ['LIVE PAYMENT EXECUTION', 'LIVE AGENT EXECUTION', 'ZERO-TRUST ENFORCED'] },
  { id: 'env_sand', name: 'SANDBOX', status: 'ACTIVE', capabilities: ['TEST EXECUTION', 'DEMO PAYMENTS', 'SIMULATED AGENTS'] },
];

export const MOCK_AUDIT_LOGS: AuditLogRecord[] = [
  { id: 'aud_1', event: 'USER.LOGIN', actor: 'admin@agentpay.io', resource: 'AUTH_SESSION', ipAddress: '103.14.88.19', timestamp: '02:14:22 UTC', status: 'SUCCESS' },
  { id: 'aud_2', event: 'MFA.ENABLED', actor: 'admin@agentpay.io', resource: 'TOTP_SECURITY', ipAddress: '103.14.88.19', timestamp: '02:10:18 UTC', status: 'SUCCESS' },
  { id: 'aud_3', event: 'ROLE.UPDATED', actor: 'lead@agentpay.io', resource: 'SECURITY_OPERATOR', ipAddress: '198.51.100.42', timestamp: '01:58:44 UTC', status: 'SUCCESS' },
];
