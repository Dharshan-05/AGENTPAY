'use client';

import { AgentTabType } from './agent-types';

interface AgentTabsProps {
  activeTab: AgentTabType;
  onTabChange: (tab: AgentTabType) => void;
}

export function AgentTabs({ activeTab, onTabChange }: AgentTabsProps) {
  const tabs: { id: AgentTabType; label: string }[] = [
    { id: 'REGISTRY', label: 'ENTERPRISE AGENT REGISTRY' },
    { id: 'EXECUTIONS', label: 'DURABLE EXECUTION LOGS' },
    { id: 'PERMISSIONS', label: 'RBAC & CAPABILITIES MATRIX' },
    { id: 'SECURITY', label: 'mTLS & SECURITY POSTURE' },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-white/[0.08] pb-3 font-mono text-xs">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2 rounded-xl font-bold transition-all ${
              isActive
                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
