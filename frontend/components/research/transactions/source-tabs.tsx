'use client';

import { TransactionSourceTabType } from './source-types';
import { Table2, FileStack, RefreshCw, ArrowLeftRight, Webhook, BookOpen } from 'lucide-react';

interface SourceTabsProps {
  activeTab: TransactionSourceTabType;
  onTabChange: (tab: TransactionSourceTabType) => void;
}

const tabs: { id: TransactionSourceTabType; label: string; icon: React.ReactNode; count?: string }[] = [
  { id: 'REGISTRY', label: 'TRANSACTION REGISTRY', icon: <Table2 className="w-3.5 h-3.5" />, count: '1,847' },
  { id: 'INTENTS', label: 'PAYMENT INTENTS', icon: <FileStack className="w-3.5 h-3.5" />, count: '1,420' },
  { id: 'LIFECYCLE', label: 'LIFECYCLE', icon: <RefreshCw className="w-3.5 h-3.5" /> },
  { id: 'REFUNDS', label: 'REFUNDS', icon: <ArrowLeftRight className="w-3.5 h-3.5" />, count: '3' },
  { id: 'EVENTS', label: 'WEBHOOK & EVENTS', icon: <Webhook className="w-3.5 h-3.5" />, count: '10' },
  { id: 'AUDIT', label: 'AUDIT TRAIL', icon: <BookOpen className="w-3.5 h-3.5" /> },
];

export function SourceTabs({ activeTab, onTabChange }: SourceTabsProps) {
  return (
    <div className="flex flex-wrap items-center gap-1.5 border-b border-slate-200 pb-0 font-sans text-xs">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-4 py-2.5 rounded-t-xl font-bold transition-all flex items-center gap-1.5 border-b-2 -mb-px ${
              isActive
                ? 'bg-white text-blue-700 border-blue-600 shadow-sm'
                : 'bg-transparent text-slate-500 hover:text-slate-800 border-transparent hover:bg-white/50'
            }`}
          >
            {tab.icon}
            {tab.label}
            {tab.count && (
              <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                isActive ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-500'
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

