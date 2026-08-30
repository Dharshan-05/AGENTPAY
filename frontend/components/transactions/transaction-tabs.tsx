'use client';

import { TxnTabType } from './transaction-types';

interface TransactionTabsProps {
  activeTab: TxnTabType;
  onTabChange: (tab: TxnTabType) => void;
  registryCount: number;
  intentCount: number;
  refundCount: number;
  eventCount: number;
  auditCount: number;
}

export function TransactionTabs({
  activeTab,
  onTabChange,
  registryCount,
  intentCount,
  refundCount,
  eventCount,
  auditCount,
}: TransactionTabsProps) {
  const tabs: { id: TxnTabType; label: string; count?: number }[] = [
    { id: 'REGISTRY', label: 'TRANSACTION LEDGER', count: registryCount },
    { id: 'INTENTS', label: 'PAYMENT INTENTS', count: intentCount },
    { id: 'LIFECYCLE', label: 'LIFECYCLE TRACKER' },
    { id: 'REFUNDS', label: 'REFUNDS LOG', count: refundCount },
    { id: 'EVENTS', label: 'EVENT STREAM', count: eventCount },
    { id: 'AUDIT', label: 'IMMUTABLE AUDIT', count: auditCount },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-white/[0.08] pb-3 font-mono text-xs">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2 rounded-xl font-bold transition-all flex items-center gap-2 ${
              isActive
                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.15)]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className={`px-1.5 py-0.5 rounded-full text-[9px] ${
                isActive ? 'bg-blue-500/20 text-blue-300' : 'bg-slate-800 text-slate-400'
              }`}>
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
