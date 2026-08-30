'use client';

import { WebhookSourceTabType } from './source-types';

interface SourceTabsProps {
  activeTab: WebhookSourceTabType;
  onTabChange: (tab: WebhookSourceTabType) => void;
  endpointCount: number;
  eventCount: number;
  deliveryCount: number;
  subscriptionCount: number;
  retryCount: number;
  auditCount: number;
}

export function SourceTabs({
  activeTab,
  onTabChange,
  endpointCount,
  eventCount,
  deliveryCount,
  subscriptionCount,
  retryCount,
  auditCount,
}: SourceTabsProps) {
  const tabs: { id: WebhookSourceTabType; label: string; count?: number }[] = [
    { id: 'REGISTRY', label: 'ENDPOINT REGISTRY', count: endpointCount },
    { id: 'EVENTS', label: 'EVENT CATALOG & LOGS', count: eventCount },
    { id: 'DELIVERIES', label: 'DELIVERY LEDGER', count: deliveryCount },
    { id: 'SUBSCRIPTIONS', label: 'SUBSCRIPTION PATTERNS', count: subscriptionCount },
    { id: 'RETRIES', label: 'RETRIES & DEAD-LETTER', count: retryCount },
    { id: 'SECURITY', label: 'SIGNATURE & mTLS SECURITY' },
    { id: 'AUDIT', label: 'IMMUTABLE AUDIT TRAIL', count: auditCount },
  ];

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-3 font-mono text-xs">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2 rounded-xl font-bold transition-all flex items-center gap-2 ${
              isActive
                ? 'bg-purple-600 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className={`px-1.5 py-0.5 rounded-full text-[9px] ${
                isActive ? 'bg-purple-800 text-purple-100' : 'bg-slate-100 text-slate-500 border border-slate-200'
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
