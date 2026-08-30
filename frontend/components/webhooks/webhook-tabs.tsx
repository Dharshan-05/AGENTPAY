'use client';

import { WebhookTabType } from './webhook-types';

interface WebhookTabsProps {
  activeTab: WebhookTabType;
  onTabChange: (tab: WebhookTabType) => void;
  registryCount: number;
  eventCount: number;
  deliveryCount: number;
  subscriptionCount: number;
  retryCount: number;
  securityCount: number;
  auditCount: number;
}

export function WebhookTabs({
  activeTab,
  onTabChange,
  registryCount,
  eventCount,
  deliveryCount,
  subscriptionCount,
  retryCount,
  securityCount,
  auditCount,
}: WebhookTabsProps) {
  const tabs: { id: WebhookTabType; label: string; count?: number }[] = [
    { id: 'REGISTRY', label: 'ENDPOINT REGISTRY', count: registryCount },
    { id: 'EVENTS', label: 'EVENT CATALOG', count: eventCount },
    { id: 'DELIVERIES', label: 'DELIVERY LEDGER', count: deliveryCount },
    { id: 'SUBSCRIPTIONS', label: 'SUBSCRIPTION PATTERNS', count: subscriptionCount },
    { id: 'RETRIES', label: 'RETRIES & DEAD-LETTER', count: retryCount },
    { id: 'SECURITY', label: 'SIGNATURE & mTLS SECURITY', count: securityCount },
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
