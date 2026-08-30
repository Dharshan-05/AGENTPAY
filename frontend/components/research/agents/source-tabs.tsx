'use client';

import { AgentSourceTabType } from './source-types';

interface SourceTabsProps {
  activeTab: AgentSourceTabType;
  onTabChange: (tab: AgentSourceTabType) => void;
}

export function SourceTabs({ activeTab, onTabChange }: SourceTabsProps) {
  const tabs: { id: AgentSourceTabType; label: string }[] = [
    { id: 'REGISTRY', label: 'ENTERPRISE AGENT REGISTRY' },
    { id: 'EXECUTIONS', label: 'DURABLE EXECUTION LOGS' },
    { id: 'PERMISSIONS', label: 'RBAC & CAPABILITIES MATRIX' },
    { id: 'SECURITY', label: 'mTLS & SECURITY POSTURE' },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-3 font-mono text-xs">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2 rounded-xl font-bold transition-all ${
              isActive
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
