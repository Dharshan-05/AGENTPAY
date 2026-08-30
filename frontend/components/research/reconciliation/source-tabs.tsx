'use client';

import { ReconciliationTabType } from './source-types';

interface SourceTabsProps {
  activeTab: ReconciliationTabType;
  onTabChange: (tab: ReconciliationTabType) => void;
}

export function SourceTabs({ activeTab, onTabChange }: SourceTabsProps) {
  const tabs: { id: ReconciliationTabType; label: string }[] = [
    { id: 'SETTLEMENTS', label: 'GATEWAY SETTLEMENT BATCHES' },
    { id: 'DISPUTES', label: 'CHARGEBACKS & DISPUTES' },
    { id: 'DISCREPANCIES', label: 'UNRESOLVED VARIANCES' },
    { id: 'AUDIT_TRAIL', label: 'IMMUTABLE AUDIT LEDGER' },
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
