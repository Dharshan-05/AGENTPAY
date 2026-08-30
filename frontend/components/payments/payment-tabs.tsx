'use client';

export type PaymentTabType =
  | 'TRANSACTIONS'
  | 'WEBHOOKS'
  | 'CHECKOUT_TESTER'
  | 'SETTLEMENTS';

interface PaymentTabsProps {
  activeTab: PaymentTabType;
  onTabChange: (tab: PaymentTabType) => void;
}

export function PaymentTabs({ activeTab, onTabChange }: PaymentTabsProps) {
  const tabs: { id: PaymentTabType; label: string }[] = [
    { id: 'TRANSACTIONS', label: 'PAYMENTS & TRANSACTIONS' },
    { id: 'WEBHOOKS', label: 'WEBHOOK & EVENT ACTIVITY' },
    { id: 'CHECKOUT_TESTER', label: 'CHECKOUT SESSION TESTER' },
    { id: 'SETTLEMENTS', label: 'SETTLEMENTS & PAYOUTS' },
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
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.15)]'
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
