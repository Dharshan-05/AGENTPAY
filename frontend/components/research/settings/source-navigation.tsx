'use client';

import { SettingsSectionType } from './source-types';
import {
  User,
  Shield,
  Smartphone,
  Building2,
  Users,
  ShieldAlert,
  Sliders,
  Globe,
  Bell,
  Activity,
  FileCode2,
} from 'lucide-react';

interface SourceNavigationProps {
  activeSection: SettingsSectionType;
  onSectionSelect: (section: SettingsSectionType) => void;
}

export function SourceNavigation({ activeSection, onSectionSelect }: SourceNavigationProps) {
  const sections: { id: SettingsSectionType; label: string; icon: any; category: string }[] = [
    { id: 'PROFILE', label: 'Account Profile', icon: User, category: 'ACCOUNT' },
    { id: 'SECURITY', label: 'Password & Auth', icon: Shield, category: 'ACCOUNT' },
    { id: 'SESSIONS', label: 'Active Sessions', icon: Smartphone, category: 'ACCOUNT' },

    { id: 'ORGANIZATION', label: 'Organization & Plan', icon: Building2, category: 'ORGANIZATION' },
    { id: 'MEMBERS', label: 'Team Members', icon: Users, category: 'ORGANIZATION' },
    { id: 'ROLES', label: 'Roles (RBAC)', icon: ShieldAlert, category: 'ORGANIZATION' },
    { id: 'PERMISSIONS', label: 'Permission Matrix', icon: Sliders, category: 'ORGANIZATION' },

    { id: 'ENVIRONMENTS', label: 'Environments', icon: Globe, category: 'SYSTEM' },
    { id: 'NOTIFICATIONS', label: 'Notifications', icon: Bell, category: 'SYSTEM' },
    { id: 'SECURITY_POSTURE', label: 'Security Health', icon: Activity, category: 'SYSTEM' },
    { id: 'AUDIT_LOG', label: 'Audit Activity', icon: FileCode2, category: 'SYSTEM' },
  ];

  const categories = Array.from(new Set(sections.map((s) => s.category)));

  return (
    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="text-xs font-bold text-slate-400 uppercase tracking-wider px-2">
        SETTINGS NAVIGATION
      </div>

      <div className="space-y-4">
        {categories.map((cat) => (
          <div key={cat} className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase px-2 tracking-wider block">
              {cat}
            </span>
            {sections
              .filter((s) => s.category === cat)
              .map((sec) => {
                const Icon = sec.icon;
                const isActive = activeSection === sec.id;
                return (
                  <button
                    key={sec.id}
                    onClick={() => onSectionSelect(sec.id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold transition-colors ${
                      isActive
                        ? 'bg-blue-50 text-blue-700 font-bold border border-blue-200 shadow-sm'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                    <span>{sec.label}</span>
                  </button>
                );
              })}
          </div>
        ))}
      </div>
    </div>
  );
}
