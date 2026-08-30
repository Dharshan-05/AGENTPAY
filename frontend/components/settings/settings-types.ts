export type ProductionSettingsTab =
  | 'ACCOUNT'
  | 'SECURITY'
  | 'SESSIONS'
  | 'ORGANIZATION'
  | 'MEMBERS'
  | 'ROLES'
  | 'PERMISSIONS'
  | 'ENVIRONMENTS'
  | 'NOTIFICATIONS'
  | 'POSTURE'
  | 'AUDIT';

export interface ProductionUserProfile {
  userId: string;
  fullName: string;
  email: string;
  role: string;
  organizationId: string;
  timezone: string;
  lastLogin: string;
  passwordLastChanged: string;
}

export interface ProductionSessionRecord {
  id: string;
  device: string;
  browser: string;
  location: string;
  ipAddress: string;
  lastActive: string;
  status: 'CURRENT' | 'ACTIVE';
}

export interface ProductionMemberRecord {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'ACTIVE' | 'INVITED' | 'SUSPENDED';
  mfaEnforced: boolean;
  joinedDate: string;
  lastActive: string;
}

export interface ProductionRoleRecord {
  id: string;
  name: string;
  membersCount: number;
  permissionsCount: number;
  environments: string;
  status: 'SYSTEM' | 'CUSTOM';
  description: string;
}

export interface ProductionPermissionRecord {
  resource: string;
  superAdmin: 'FULL' | 'WRITE' | 'READ' | 'DENIED';
  securityOperator: 'FULL' | 'WRITE' | 'READ' | 'DENIED';
  developer: 'FULL' | 'WRITE' | 'READ' | 'DENIED';
  analyst: 'FULL' | 'WRITE' | 'READ' | 'DENIED';
}

export interface ProductionEnvironmentRecord {
  id: string;
  name: 'PRODUCTION' | 'SANDBOX';
  status: 'LIVE' | 'SAFE';
  capabilities: string[];
}

export interface ProductionAuditEventRecord {
  id: string;
  timestamp: string;
  event: string;
  actor: string;
  resource: string;
  ipAddress: string;
  result: 'SUCCESS' | 'FAILED' | 'BLOCKED';
  auditHash: string;
}
