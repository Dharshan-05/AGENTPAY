'use client';

import { useState } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { SettingsHeader } from '@/components/settings/settings-header';
import { SettingsNavigation } from '@/components/settings/settings-navigation';
import { SettingsProfile } from '@/components/settings/settings-profile';
import { SettingsSecurity } from '@/components/settings/settings-security';
import { SettingsSessions } from '@/components/settings/settings-sessions';
import { SettingsOrganization } from '@/components/settings/settings-organization';
import { SettingsMembers } from '@/components/settings/settings-members';
import { MemberInspector } from '@/components/settings/member-inspector';
import { InviteMemberModal } from '@/components/settings/invite-member-modal';
import { SettingsRoles } from '@/components/settings/settings-roles';
import { RoleInspector } from '@/components/settings/role-inspector';
import { SettingsPermissions } from '@/components/settings/settings-permissions';
import { SettingsEnvironments } from '@/components/settings/settings-environments';
import { SettingsNotifications } from '@/components/settings/settings-notifications';
import { SecurityPosture } from '@/components/settings/security-posture';
import { SettingsAudit } from '@/components/settings/settings-audit';
import { AuditInspector } from '@/components/settings/audit-inspector';

import {
  ProductionSettingsTab,
  ProductionUserProfile,
  ProductionSessionRecord,
  ProductionMemberRecord,
  ProductionRoleRecord,
  ProductionAuditEventRecord,
} from '@/components/settings/settings-types';

import {
  INITIAL_USER_PROFILE,
  INITIAL_SESSIONS,
  INITIAL_MEMBERS,
  INITIAL_ROLES,
  INITIAL_PERMISSIONS,
  INITIAL_ENVIRONMENTS,
  INITIAL_AUDIT_LOGS,
} from '@/components/settings/settings-data';

export default function ProductionSettingsPage() {
  const [activeTab, setActiveTab] = useState<ProductionSettingsTab>('ACCOUNT');
  const [currentEnv, setCurrentEnv] = useState<'PRODUCTION' | 'SANDBOX'>('PRODUCTION');

  // State
  const [userProfile, setUserProfile] = useState<ProductionUserProfile>(INITIAL_USER_PROFILE);
  const [sessions, setSessions] = useState<ProductionSessionRecord[]>(INITIAL_SESSIONS);
  const [members, setMembers] = useState<ProductionMemberRecord[]>(INITIAL_MEMBERS);
  const [roles] = useState<ProductionRoleRecord[]>(INITIAL_ROLES);
  const [permissions] = useState(INITIAL_PERMISSIONS);
  const [environments, setEnvironments] = useState(INITIAL_ENVIRONMENTS);
  const [auditLogs, setAuditLogs] = useState<ProductionAuditEventRecord[]>(INITIAL_AUDIT_LOGS);

  // Inspector & Modal State
  const [selectedMember, setSelectedMember] = useState<ProductionMemberRecord | null>(null);
  const [selectedRole, setSelectedRole] = useState<ProductionRoleRecord | null>(null);
  const [selectedAuditLog, setSelectedAuditLog] = useState<ProductionAuditEventRecord | null>(null);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState<boolean>(false);

  const handleSaveProfile = (name: string, email: string) => {
    setUserProfile((prev) => ({ ...prev, fullName: name, email }));
  };

  const handleRevokeSession = (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id));
  };

  const handleRevokeAllOtherSessions = () => {
    setSessions((prev) => prev.filter((s) => s.status === 'CURRENT'));
  };

  const handleInviteMember = (name: string, email: string, role: string) => {
    const newMember: ProductionMemberRecord = {
      id: `usr_${Math.random().toString(36).substring(2, 6)}`,
      name,
      email,
      role,
      status: 'INVITED',
      mfaEnforced: false,
      joinedDate: new Date().toISOString().substring(0, 10),
      lastActive: 'Never',
    };
    setMembers((prev) => [...prev, newMember]);
  };

  const handleSuspendMember = (id: string) => {
    setMembers((prev) =>
      prev.map((m) => (m.id === id ? { ...m, status: 'SUSPENDED' as const } : m))
    );
  };

  return (
    <AgentPayShell activeTab="settings">
      <div className="space-y-6 pb-12">
        
        {/* HEADER */}
        <SettingsHeader
          currentEnv={currentEnv}
          onEnvChange={setCurrentEnv}
          onSave={() => alert('Settings configuration saved successfully')}
          onExport={() => alert('Exporting security audit log...')}
        />

        {/* TWO-COLUMN CONTROL PLANE LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* LEFT SIDEBAR NAVIGATION */}
          <div className="lg:col-span-1">
            <SettingsNavigation activeTab={activeTab} onTabChange={setActiveTab} />
          </div>

          {/* MAIN SETTINGS CONTENT AREA */}
          <div className="lg:col-span-3 space-y-6">
            {activeTab === 'ACCOUNT' && (
              <SettingsProfile profile={userProfile} onSaveProfile={handleSaveProfile} />
            )}

            {activeTab === 'SECURITY' && <SettingsSecurity />}

            {activeTab === 'SESSIONS' && (
              <SettingsSessions
                sessions={sessions}
                onRevokeSession={handleRevokeSession}
                onRevokeAllOtherSessions={handleRevokeAllOtherSessions}
              />
            )}

            {activeTab === 'ORGANIZATION' && <SettingsOrganization />}

            {activeTab === 'MEMBERS' && (
              <SettingsMembers
                members={members}
                onSelectMember={(m) => setSelectedMember(m)}
                onOpenInviteModal={() => setIsInviteModalOpen(true)}
                onSuspendMember={handleSuspendMember}
              />
            )}

            {activeTab === 'ROLES' && (
              <SettingsRoles roles={roles} onSelectRole={(r) => setSelectedRole(r)} />
            )}

            {activeTab === 'PERMISSIONS' && (
              <SettingsPermissions permissions={permissions} />
            )}

            {activeTab === 'ENVIRONMENTS' && (
              <SettingsEnvironments
                environments={environments}
                currentEnv={currentEnv}
                onSwitchEnv={setCurrentEnv}
              />
            )}

            {activeTab === 'NOTIFICATIONS' && <SettingsNotifications />}

            {activeTab === 'POSTURE' && <SecurityPosture />}

            {activeTab === 'AUDIT' && (
              <SettingsAudit logs={auditLogs} onSelectAudit={(l) => setSelectedAuditLog(l)} />
            )}
          </div>

        </div>

        {/* INVITE MEMBER MODAL */}
        <InviteMemberModal
          isOpen={isInviteModalOpen}
          onClose={() => setIsInviteModalOpen(false)}
          onInvite={handleInviteMember}
        />

        {/* MEMBER INSPECTOR DRAWER */}
        <MemberInspector
          member={selectedMember}
          onClose={() => setSelectedMember(null)}
          onSuspend={handleSuspendMember}
        />

        {/* ROLE INSPECTOR DRAWER */}
        <RoleInspector
          role={selectedRole}
          onClose={() => setSelectedRole(null)}
        />

        {/* AUDIT INSPECTOR DRAWER */}
        <AuditInspector
          audit={selectedAuditLog}
          onClose={() => setSelectedAuditLog(null)}
        />

      </div>
    </AgentPayShell>
  );
}
