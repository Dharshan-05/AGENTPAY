'use client';

import { useState } from 'react';
import { Search, ShieldAlert, AlertOctagon, Activity, Radio, Check } from 'lucide-react';
import { AGButton } from '@/components/ui/ag-button';

interface TopNavProps {
  onEmergencyFreeze?: () => void;
}

export function AgentPayTopNav({ onEmergencyFreeze }: TopNavProps) {
  const [frozen, setFrozen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleFreeze = () => {
    setFrozen(!frozen);
    if (onEmergencyFreeze) onEmergencyFreeze();
  };

  return (
    <header className="h-16 px-6 border-b border-white/[0.08] bg-slate-950/80 backdrop-blur-xl flex items-center justify-between z-20 shrink-0">
      {/* Global Search */}
      <div className="flex items-center gap-4 flex-1 max-w-md">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search agents, policies, transactions, risk signals..."
            className="w-full pl-10 pr-4 py-2 bg-slate-900/80 border border-white/10 rounded-xl text-xs font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50 transition-all"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Environment & Security Status */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-white/[0.06] font-mono text-[11px]">
          <span className="inline-flex items-center gap-1.5 text-emerald-400 font-bold">
            <Radio className="w-3 h-3 animate-pulse" /> MAINNET v2.4
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">ZERO-TRUST ENFORCED</span>
        </div>

        {/* Emergency Freeze Button */}
        <button
          onClick={handleFreeze}
          className={`px-3.5 py-1.5 rounded-xl font-mono text-xs font-bold flex items-center gap-2 transition-all ${
            frozen
              ? 'bg-red-600 text-white shadow-[0_0_20px_rgba(239,68,68,0.5)] border border-red-400'
              : 'bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20'
          }`}
        >
          <AlertOctagon className="w-3.5 h-3.5" />
          <span>{frozen ? 'SYSTEM FROZEN' : 'EMERGENCY FREEZE'}</span>
        </button>

        {/* Admin Avatar */}
        <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-mono text-xs font-bold">
          AG
        </div>
      </div>
    </header>
  );
}
