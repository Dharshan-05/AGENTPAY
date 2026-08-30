'use client';

import { PaymentMethodTabType } from './payment-method-types';

interface PaymentMethodTabsProps {
  activeTab: PaymentMethodTabType;
  onTabChange: (tab: PaymentMethodTabType) => void;
  registryCount: number;
  catalogCount: number;
  cardsBanksCount: number;
  processorsCount: number;
  routingCount: number;
  securityCount: number;
  riskCount: number;
  auditCount: number;
}

export function PaymentMethodTabs({
  activeTab,
  onTabChange,
  registryCount,
  catalogCount,
  cardsBanksCount,
  processorsCount,
  routingCount,
  securityCount,
  riskCount,
  auditCount,
}: PaymentMethodTabsProps) {
  const tabs: { id: PaymentMethodTabType; label: string; count?: number }[] = [
    { id: 'REGISTRY', label: 'REGISTRY', count: registryCount },
    { id: 'CATALOG', label: 'CATALOG', count: catalogCount },
    { id: 'CARDS_BANKS', label: 'CARDS / BANKS', count: cardsBanksCount },
    { id: 'PROCESSORS', label: 'PROCESSORS', count: processorsCount },
    { id: 'ROUTING', label: 'ROUTING', count: routingCount },
    { id: 'SECURITY', label: 'SECURITY', count: securityCount },
    { id: 'RISK', label: 'RISK', count: riskCount },
    { id: 'AUDIT', label: 'AUDIT', count: auditCount },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-white/[0.08] pb-3 font-mono text-xs">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-3.5 py-1.5 rounded-xl transition-all font-semibold flex items-center gap-1.5 ${
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
