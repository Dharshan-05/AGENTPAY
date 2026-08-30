'use client';

import { useState, useEffect } from 'react';
import { ShieldCheck, Search, AlertOctagon, Activity, Radio, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface HeaderProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onEmergencyFreeze: () => void;
}

export function CommandHeader({ searchQuery, onSearchChange, onEmergencyFreeze }: HeaderProps) {
  const [time, setTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC');
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-40 bg-slate-950/90 backdrop-blur-2xl border-b border-white/[0.08] px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        {/* Left: Brand & Page Title */}
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="w-8 h-8 rounded-lg bg-slate-900 border border-white/10 flex items-center justify-center text-slate-400 hover:text-white hover:border-emerald-500/40 transition-all"
            title="Return to Landing Page"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.2)]">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display font-bold text-lg text-slate-100 tracking-wider">
                COMMAND <span className="text-emerald-400">CENTER</span>
              </h1>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[9px] uppercase tracking-widest flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Ops
              </span>
            </div>
            <p className="text-[10px] font-mono text-slate-400">
              Autonomous Agent Financial Governance & Risk Telemetry
            </p>
          </div>
        </div>

        {/* Middle: Search & Telemetry Metadata */}
        <div className="flex items-center gap-4 flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search Agent ID, Intent, Policy, or Hash..."
              className="w-full bg-slate-900/80 border border-white/[0.1] rounded-xl pl-9 pr-4 py-2 text-xs font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30 transition-all"
            />
          </div>
        </div>

        {/* Right: Clock & Security Action */}
        <div className="flex items-center gap-4 justify-between md:justify-end">
          <div className="hidden xl:flex flex-col text-right font-mono text-[10px] text-slate-400">
            <span className="text-slate-200 font-semibold flex items-center gap-1 justify-end">
              <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
              US-EAST-PRIMARY
            </span>
            <span>{time || '2026-08-30 00:40:00 UTC'}</span>
          </div>

          <button
            onClick={onEmergencyFreeze}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 text-red-400 hover:text-red-300 font-mono text-xs uppercase tracking-wider font-semibold transition-all shadow-[0_0_15px_rgba(239,68,68,0.15)]"
          >
            <AlertOctagon className="w-4 h-4 text-red-400" />
            Freeze All Agents
          </button>
        </div>

      </div>
    </header>
  );
}
