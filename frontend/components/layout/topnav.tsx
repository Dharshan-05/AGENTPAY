'use client';

import { useState } from 'react';
import { Search, Bell, AlertOctagon, Check, Globe } from 'lucide-react';

interface TopNavProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onEmergencyFreeze: () => void;
}

export function TopNav({ searchQuery, onSearchChange, onEmergencyFreeze }: TopNavProps) {
  const [showAlerts, setShowAlerts] = useState(false);

  const ALERTS = [
    { id: 1, title: 'Anomalous Wire Request Blocked', time: '2m ago', severity: 'HIGH' },
    { id: 2, title: 'Ad Campaign Spend Velocity High', time: '14m ago', severity: 'MEDIUM' },
    { id: 3, title: 'AGENTGUARD Policy v2.4 Active', time: '1h ago', severity: 'INFO' },
  ];

  return (
    <header className="h-16 bg-slate-950/90 backdrop-blur-xl border-b border-white/[0.08] px-6 flex items-center justify-between gap-4 sticky top-0 z-30">
      {/* Global Search */}
      <div className="flex items-center gap-3 flex-1 max-w-lg">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Agent ID, Intent, Policy, Hash, or Transaction..."
            className="w-full bg-slate-900/80 border border-white/[0.1] rounded-xl pl-10 pr-4 py-2 text-xs font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30 transition-all"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Environment Tag */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">
          <Globe className="w-3 h-3" /> PRODUCTION
        </div>

        {/* Security Alerts Button */}
        <div className="relative">
          <button
            onClick={() => setShowAlerts(!showAlerts)}
            className="relative p-2 rounded-xl bg-slate-900 border border-white/10 text-slate-400 hover:text-slate-100 transition-colors"
            title="Notifications & Security Intelligence"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-slate-950 font-mono text-[9px] font-bold flex items-center justify-center animate-pulse">
              3
            </span>
          </button>

          {showAlerts && (
            <div className="absolute right-0 mt-2 w-80 bg-slate-950 border border-white/10 rounded-2xl shadow-2xl p-4 z-50 font-mono">
              <div className="flex items-center justify-between pb-3 border-b border-white/[0.08] mb-3 text-xs">
                <span className="font-bold text-slate-200">FRAUDGUARD INTELLIGENCE</span>
                <span className="text-[10px] text-amber-400">3 UNREAD ALERTS</span>
              </div>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {ALERTS.map((a) => (
                  <div key={a.id} className="p-2.5 rounded-lg bg-slate-900/60 border border-white/[0.06] text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-slate-200">{a.title}</span>
                      <span className="text-[9px] text-slate-500">{a.time}</span>
                    </div>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded uppercase font-bold ${
                        a.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
                      }`}
                    >
                      {a.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User / Organization Profile */}
        <div className="flex items-center gap-3 pl-2 border-l border-white/[0.08]">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-mono font-bold text-xs">
            SEC
          </div>
          <div className="hidden lg:flex flex-col text-left">
            <span className="text-xs font-mono font-bold text-slate-200">SecOps Admin</span>
            <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1">
              <Check className="w-3 h-3" /> Authenticated
            </span>
          </div>
        </div>

        {/* Emergency Freeze Button */}
        <button
          onClick={onEmergencyFreeze}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 font-mono text-xs font-semibold uppercase tracking-wider transition-all"
        >
          <AlertOctagon className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Emergency Freeze</span>
        </button>
      </div>
    </header>
  );
}
