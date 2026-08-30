'use client';

import { PaymentMethodSourceTabType } from './source-types';

interface SourceTabsProps {
  activeTab: PaymentMethodSourceTabType;
  onTabChange: (tab: PaymentMethodSourceTabType) => void;
  registryCount: number;
  catalogCount: number;
  cardsBanksCount: number;
  matrixCount: number;
  routingCount: number;
  securityCount: number;
  riskCount: number;
  auditCount: number;
}

export function SourceTabs({
  activeTab,
  onTabChange,
  registryCount,
  catalogCount,
  cardsBanksCount,
  matrixCount,
  routingCount,
  securityCount,
  riskCount,
  auditCount,
}: SourceTabsProps) {
  const tabs: { id: PaymentMethodSourceTabType; label: string; count?: number }[] = [
    { id: 'REGISTRY', label: 'METHOD REGISTRY', count: registryCount },
    { id: 'CATALOG', label: 'METHOD CATALOG', count: catalogCount },
    { id: 'CARDS_BANKS', label: 'CARDS & BANKS', count: cardsBanksCount },
    { id: 'MATRIX', label: 'PROCESSOR MATRIX', count: matrixCount },
    { id: 'ROUTING', label: 'SMART ROUTING', count: routingCount },
    { id: 'SECURITY', label: 'TOKEN & PCI SECURITY', count: securityCount },
    { id: 'RISK', label: 'FRAUDGUARD RISK', count: riskCount },
    { id: 'AUDIT', label: 'IMMUTABLE AUDIT TRAIL', count: auditCount },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-white/[0.08] pb-3 font-mono text-xs">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-3 py-1.5 rounded-xl transition-all font-semibold flex items-center gap-1.5 ${
              isActive
                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30 shadow-[0_0_12px_rgba(59,130,246,0.15)]'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
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
