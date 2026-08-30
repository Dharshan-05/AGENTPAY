export type SettingsSectionType =
  | 'PROFILE'
  | 'SECURITY'
  | 'SESSIONS'
  | 'ORGANIZATION'
  | 'MEMBERS'
  | 'ROLES'
  | 'PERMISSIONS'
  | 'ENVIRONMENTS'
  | 'NOTIFICATIONS'
  | 'SECURITY_POSTURE'
  | 'AUDIT_LOG';

export interface UserProfile {
  fullName: string;
  email: string;
  role: string;
  timezone: string;
  language: string;
  theme: string;
}

export interface SecuritySetting {
  mfaEnabled: boolean;
  passwordLastChanged: string;
  ipRestrictionEnabled: boolean;
  zeroTrustStatus: string;
}

export interface ActiveSessionRecord {
  id: string;
  device: string;
  browser: string;
  location: string;
  ipAddress: string;
  lastActive: string;
  status: 'CURRENT' | 'ACTIVE';
}

export interface OrganizationDetails {
  name: string;
  id: string;
  workspace: string;
  plan: string;
  membersCount: number;
  securityMode: string;
}

export interface OrganizationMemberRecord {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'ACTIVE' | 'INVITED' | 'SUSPENDED';
  lastActive: string;
}

export interface RoleRecord {
  id: string;
  name: string;
  membersCount: number;
  permissionsCount: number;
  status: 'SYSTEM' | 'CUSTOM';
  description: string;
}

export interface PermissionRecord {
  resource: string;
  superAdmin: string;
  securityOperator: string;
  developer: string;
  analyst: string;
  viewer: string;
}

export interface EnvironmentRecord {
  id: string;
  name: 'PRODUCTION' | 'SANDBOX';
  status: 'ACTIVE' | 'PAUSED';
  capabilities: string[];
}

export interface NotificationPreferenceRecord {
  id: string;
  category: string;
  email: boolean;
  inApp: boolean;
  webhook: boolean;
}

export interface SecurityControlRecord {
  name: string;
  status: 'ENABLED' | 'WARNING' | 'DISABLED';
  detail: string;
}

export interface AuditLogRecord {
  id: string;
  event: string;
  actor: string;
  resource: string;
  ipAddress: string;
  timestamp: string;
  status: 'SUCCESS' | 'FAILED';
}
