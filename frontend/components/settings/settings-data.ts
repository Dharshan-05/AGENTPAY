import {
  ProductionUserProfile,
  ProductionSessionRecord,
  ProductionMemberRecord,
  ProductionRoleRecord,
  ProductionPermissionRecord,
  ProductionEnvironmentRecord,
  ProductionAuditEventRecord,
} from './settings-types';

export const INITIAL_USER_PROFILE: ProductionUserProfile = {
  userId: 'USR-AGP-00421',
  fullName: 'Security Administrator',
  email: 'admin@agentpay.io',
  role: 'SUPER ADMIN',
  organizationId: 'ORG-AGP-001',
  timezone: 'UTC (Coordinated Universal Time)',
  lastLogin: 'Just now (10.24.xxx.xxx)',
  passwordLastChanged: '14 days ago (90-day rotation compliant)',
};

export const INITIAL_SESSIONS: ProductionSessionRecord[] = [
  {
    id: 'SES-9F82A1',
    device: 'Windows Workstation',
    browser: 'Chrome / Windows',
    location: 'Coimbatore, IN',
    ipAddress: '10.24.xxx.xxx',
    lastActive: 'Just now',
    status: 'CURRENT',
  },
  {
    id: 'SES-7A31D4',
    device: 'MacBook Pro 16"',
    browser: 'Safari / macOS',
    location: 'Bengaluru, IN',
    ipAddress: '10.25.xxx.xxx',
    lastActive: '18 min ago',
    status: 'ACTIVE',
  },
];

export const INITIAL_MEMBERS: ProductionMemberRecord[] = [
  { id: 'usr_1', name: 'Security Administrator', email: 'admin@agentpay.io', role: 'SUPER ADMIN', status: 'ACTIVE', mfaEnforced: true, joinedDate: '2026-01-10', lastActive: 'Just now' },
  { id: 'usr_2', name: 'Platform Lead', email: 'lead@agentpay.io', role: 'SECURITY OPERATOR', status: 'ACTIVE', mfaEnforced: true, joinedDate: '2026-02-14', lastActive: '12 min ago' },
  { id: 'usr_3', name: 'Fraud Intelligence Analyst', email: 'fraud@agentpay.io', role: 'ANALYST', status: 'ACTIVE', mfaEnforced: true, joinedDate: '2026-03-01', lastActive: '1 hour ago' },
  { id: 'usr_4', name: 'Developer Integrator', email: 'dev@agentpay.io', role: 'DEVELOPER', status: 'INVITED', mfaEnforced: false, joinedDate: '2026-08-20', lastActive: 'Never' },
];

export const INITIAL_ROLES: ProductionRoleRecord[] = [
  { id: 'rol_super', name: 'SUPER ADMIN', membersCount: 4, permissionsCount: 42, environments: 'PRODUCTION + SANDBOX', status: 'SYSTEM', description: 'Unconstrained security, policy, and infrastructure management access.' },
  { id: 'rol_secops', name: 'SECURITY OPERATOR', membersCount: 8, permissionsCount: 31, environments: 'PRODUCTION + SANDBOX', status: 'SYSTEM', description: 'AgentGuard, FraudGuard, and risk policy intervention control.' },
  { id: 'rol_dev', name: 'DEVELOPER', membersCount: 42, permissionsCount: 18, environments: 'SANDBOX + LIMITED PROD', status: 'SYSTEM', description: 'API token generation, webhooks, and SDK sandbox testing.' },
  { id: 'rol_analyst', name: 'ANALYST', membersCount: 74, permissionsCount: 12, environments: 'READ ONLY', status: 'CUSTOM', description: 'Financial analytics, transaction telemetry, and audit inspection.' },
];

export const INITIAL_PERMISSIONS: ProductionPermissionRecord[] = [
  { resource: 'PAYMENTS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'WRITE', analyst: 'READ' },
  { resource: 'AGENTS', superAdmin: 'FULL', securityOperator: 'WRITE', developer: 'READ', analyst: 'READ' },
  { resource: 'AGENTGUARD', superAdmin: 'FULL', securityOperator: 'FULL', developer: 'READ', analyst: 'READ' },
  { resource: 'FRAUDGUARD', superAdmin: 'FULL', securityOperator: 'FULL', developer: 'READ', analyst: 'READ' },
  { resource: 'ANALYTICS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'READ', analyst: 'FULL' },
  { resource: 'DEVELOPERS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'FULL', analyst: 'DENIED' },
  { resource: 'SETTINGS', superAdmin: 'FULL', securityOperator: 'READ', developer: 'DENIED', analyst: 'DENIED' },
];

export const INITIAL_ENVIRONMENTS: ProductionEnvironmentRecord[] = [
  { id: 'env_prod', name: 'PRODUCTION', status: 'LIVE', capabilities: ['LIVE TRANSACTION EXECUTION', 'LIVE AGENT EXECUTION', 'LIVE API ACCESS', 'ZERO-TRUST ENFORCED'] },
  { id: 'env_sand', name: 'SANDBOX', status: 'SAFE', capabilities: ['DEMO TRANSACTIONS', 'TESTING PLAYGROUND', 'DEVELOPER SIMULATION', 'NON-MONETARY EXECUTION'] },
];

export const INITIAL_AUDIT_LOGS: ProductionAuditEventRecord[] = [
  { id: 'aud_82F1', timestamp: '09:42:18 UTC', event: 'USER.LOGIN', actor: 'USR-AGP-00421', resource: 'ACCOUNT', ipAddress: '10.24.xxx.xxx', result: 'SUCCESS', auditHash: '0x82F100281F7A9B84110298' },
  { id: 'aud_71D2', timestamp: '09:37:11 UTC', event: 'MFA.ENABLED', actor: 'USR-AGP-00421', resource: 'SECURITY', ipAddress: '10.24.xxx.xxx', result: 'SUCCESS', auditHash: '0x71D29912019A8271C88192' },
  { id: 'aud_65AC', timestamp: '09:12:48 UTC', event: 'ROLE.UPDATED', actor: 'USR-AGP-00102', resource: 'MEMBER', ipAddress: '10.25.xxx.xxx', result: 'SUCCESS', auditHash: '0x65AC7B12E8890281C99018' },
];
