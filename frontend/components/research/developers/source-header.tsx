'use client';

import { Code2, Key, Terminal, Webhook, FileCode2, Plus } from 'lucide-react';

interface SourceHeaderProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onOpenCreateKeyModal: () => void;
}

export function SourceHeader({ activeTab, onTabChange, onOpenCreateKeyModal }: SourceHeaderProps) {
  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      
      {/* SOURCE REPOSITORY ATTRIBUTION BANNER */}
      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-blue-100 text-blue-800 font-bold rounded text-[10px] uppercase">
            SOURCE EXCAVATION REFERENCE
          </span>
          <span className="font-semibold text-slate-700">Repository:</span>
          <span className="font-mono text-slate-600 text-[11px]">stripe/developer-dashboard-ui</span>
        </div>
        <span className="text-[10px] text-slate-500 font-medium">Route: /research/developers-source</span>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Code2 className="w-6 h-6 text-blue-600" />
            Developer Platform & API Console Source UI
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Excavated developer dashboard architecture reproducing API Key management, webhook subscriptions, SDK sandbox testing, and request logs.
          </p>
        </div>

        <button
          onClick={onOpenCreateKeyModal}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create New API Key
        </button>
      </div>

      {/* TABS SWITCHER */}
      <div className="flex items-center gap-2 border-b border-slate-200 pt-2 text-xs font-medium">
        {[
          { id: 'KEYS', label: 'API Keys & Secrets', icon: Key },
          { id: 'WEBHOOKS', label: 'Webhooks & Events', icon: Webhook },
          { id: 'SDK_TESTER', label: 'SDK Interactive Tester', icon: Terminal },
          { id: 'LOGS', label: 'Request & Audit Logs', icon: FileCode2 },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`pb-3 px-3 font-semibold flex items-center gap-1.5 border-b-2 transition-colors ${
                isActive
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
