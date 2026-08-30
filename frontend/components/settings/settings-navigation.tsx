'use client';

import { ProductionSettingsTab } from './settings-types';
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

interface SettingsNavigationProps {
  activeTab: ProductionSettingsTab;
  onTabChange: (tab: ProductionSettingsTab) => void;
}

export function SettingsNavigation({ activeTab, onTabChange }: SettingsNavigationProps) {
  const categories: {
    category: string;
    items: { id: ProductionSettingsTab; label: string; icon: any }[];
  }[] = [
    {
      category: 'IDENTITY & ACCOUNT',
      items: [
        { id: 'ACCOUNT', label: 'Account Profile', icon: User },
        { id: 'SECURITY', label: 'Security & Auth', icon: Shield },
        { id: 'SESSIONS', label: 'Active Sessions', icon: Smartphone },
      ],
    },
    {
      category: 'ORGANIZATION & ACCESS',
      items: [
        { id: 'ORGANIZATION', label: 'Organization & Plan', icon: Building2 },
        { id: 'MEMBERS', label: 'Team Members', icon: Users },
        { id: 'ROLES', label: 'Roles & RBAC', icon: ShieldAlert },
        { id: 'PERMISSIONS', label: 'Permission Matrix', icon: Sliders },
      ],
    },
    {
      category: 'SYSTEM & CONTROL',
      items: [
        { id: 'ENVIRONMENTS', label: 'Environments', icon: Globe },
        { id: 'NOTIFICATIONS', label: 'Notifications', icon: Bell },
        { id: 'POSTURE', label: 'Security Posture', icon: Activity },
        { id: 'AUDIT', label: 'Audit Telemetry', icon: FileCode2 },
      ],
    },
  ];

  return (
    <div className="rounded-2xl border border-white/[0.08] bg-slate-900/60 p-4 backdrop-blur-xl space-y-4 font-mono text-xs shadow-2xl">
      <div className="text-[10px] text-slate-400 font-bold uppercase tracking-wider px-2">
        CONTROL PLANE SECTIONS
      </div>

      <div className="space-y-4">
        {categories.map((cat) => (
          <div key={cat.category} className="space-y-1">
            <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider px-2 block">
              {cat.category}
            </span>
            {cat.items.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold transition-all text-left ${
                    isActive
                      ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
