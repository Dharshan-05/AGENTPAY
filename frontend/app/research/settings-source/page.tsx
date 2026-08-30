'use client';

import { useState } from 'react';
import './settings-source.css';
import { SourceHeader } from '@/components/research/settings/source-header';
import { SourceNavigation } from '@/components/research/settings/source-navigation';
import { SourceProfile } from '@/components/research/settings/source-profile';
import { SourceSecurity } from '@/components/research/settings/source-security';
import { SourceSessions } from '@/components/research/settings/source-sessions';
import { SourceOrganization } from '@/components/research/settings/source-organization';
import { SourceMembers } from '@/components/research/settings/source-members';
import { SourceRoles } from '@/components/research/settings/source-roles';
import { SourcePermissions } from '@/components/research/settings/source-permissions';
import { SourceEnvironments } from '@/components/research/settings/source-environments';
import { SourceNotifications } from '@/components/research/settings/source-notifications';
import { SourceSecurityPosture } from '@/components/research/settings/source-security-posture';
import { SourceAudit } from '@/components/research/settings/source-audit';
import { SourceModals } from '@/components/research/settings/source-modals';
import { SourceInspector } from '@/components/research/settings/source-inspector';

import {
  SettingsSectionType,
  OrganizationMemberRecord,
  RoleRecord,
  AuditLogRecord,
  ActiveSessionRecord,
} from '@/components/research/settings/source-types';

import {
  MOCK_PROFILE,
  MOCK_SESSIONS,
  MOCK_MEMBERS,
  MOCK_ROLES,
  MOCK_PERMISSIONS,
  MOCK_ENVIRONMENTS,
  MOCK_AUDIT_LOGS,
} from '@/components/research/settings/source-data';

export default function SettingsSourceResearchPage() {
  const [activeSection, setActiveSection] = useState<SettingsSectionType>('PROFILE');
  const [sessions, setSessions] = useState<ActiveSessionRecord[]>(MOCK_SESSIONS);
  const [members, setMembers] = useState<OrganizationMemberRecord[]>(MOCK_MEMBERS);
  const [roles] = useState<RoleRecord[]>(MOCK_ROLES);
  const [auditLogs] = useState<AuditLogRecord[]>(MOCK_AUDIT_LOGS);

  // Inspector & Modal State
  const [selectedMember, setSelectedMember] = useState<OrganizationMemberRecord | null>(null);
  const [selectedRole, setSelectedRole] = useState<RoleRecord | null>(null);
  const [selectedAuditLog, setSelectedAuditLog] = useState<AuditLogRecord | null>(null);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState<boolean>(false);

  const handleRevokeSession = (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id));
  };

  const handleRevokeAllOtherSessions = () => {
    setSessions((prev) => prev.filter((s) => s.status === 'CURRENT'));
  };

  const handleInviteMember = (email: string, role: string) => {
    const newMember: OrganizationMemberRecord = {
      id: `usr_${Math.random().toString(36).substring(2, 6)}`,
      name: email.split('@')[0],
      email,
      role,
      status: 'INVITED',
      lastActive: 'Never',
    };
    setMembers((prev) => [...prev, newMember]);
  };

  return (
    <div className="settings-source-root min-h-screen p-6 space-y-6 bg-slate-100 font-sans">
      
      {/* HEADER */}
      <SourceHeader
        onSave={() => alert('Settings changes saved cleanly')}
        onReset={() => setActiveSection('PROFILE')}
      />

      {/* TWO-COLUMN SETTINGS WORKSPACE */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* LEFT NAVIGATION */}
        <div className="lg:col-span-1">
          <SourceNavigation
            activeSection={activeSection}
            onSectionSelect={setActiveSection}
          />
        </div>

        {/* RIGHT CONTENT SECTION */}
        <div className="lg:col-span-3 space-y-6">
          {activeSection === 'PROFILE' && <SourceProfile profile={MOCK_PROFILE} />}

          {activeSection === 'SECURITY' && <SourceSecurity />}

          {activeSection === 'SESSIONS' && (
            <SourceSessions
              sessions={sessions}
              onRevokeSession={handleRevokeSession}
              onRevokeAllOtherSessions={handleRevokeAllOtherSessions}
            />
          )}

          {activeSection === 'ORGANIZATION' && <SourceOrganization />}

          {activeSection === 'MEMBERS' && (
            <SourceMembers
              members={members}
              onSelectMember={(m) => setSelectedMember(m)}
              onOpenInviteModal={() => setIsInviteModalOpen(true)}
            />
          )}

          {activeSection === 'ROLES' && (
            <SourceRoles
              roles={roles}
              onSelectRole={(r) => setSelectedRole(r)}
            />
          )}

          {activeSection === 'PERMISSIONS' && (
            <SourcePermissions permissions={MOCK_PERMISSIONS} />
          )}

          {activeSection === 'ENVIRONMENTS' && (
            <SourceEnvironments environments={MOCK_ENVIRONMENTS} />
          )}

          {activeSection === 'NOTIFICATIONS' && <SourceNotifications />}

          {activeSection === 'SECURITY_POSTURE' && <SourceSecurityPosture />}

          {activeSection === 'AUDIT_LOG' && (
            <SourceAudit
              logs={auditLogs}
              onSelectLog={(l) => setSelectedAuditLog(l)}
            />
          )}
        </div>

      </div>

      {/* INVITE MODAL */}
      <SourceModals
        isInviteOpen={isInviteModalOpen}
        onCloseInvite={() => setIsInviteModalOpen(false)}
        onInviteMember={handleInviteMember}
      />

      {/* INSPECTOR DRAWER */}
      <SourceInspector
        memberItem={selectedMember}
        roleItem={selectedRole}
        auditItem={selectedAuditLog}
        onClose={() => {
          setSelectedMember(null);
          setSelectedRole(null);
          setSelectedAuditLog(null);
        }}
      />

    </div>
  );
}
