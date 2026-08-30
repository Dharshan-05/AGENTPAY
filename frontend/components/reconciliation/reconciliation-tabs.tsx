'use client';

import { ReconciliationTabType } from './reconciliation-types';

interface ReconciliationTabsProps {
  activeTab: ReconciliationTabType;
  onTabChange: (tab: ReconciliationTabType) => void;
}

export function ReconciliationTabs({ activeTab, onTabChange }: ReconciliationTabsProps) {
  const tabs: { id: ReconciliationTabType; label: string }[] = [
    { id: 'SETTLEMENTS', label: 'GATEWAY SETTLEMENTS' },
    { id: 'DISPUTES', label: 'CHARGEBACKS & DISPUTES' },
    { id: 'DISCREPANCIES', label: 'UNRESOLVED VARIANCES' },
    { id: 'AUDIT', label: 'IMMUTABLE AUDIT TRAIL' },
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
