'use client';

import { useState } from 'react';
import { Activity, TrendingUp, Cpu, Radio } from 'lucide-react';

export function LiveOperationsChart() {
  const [timeframe, setTimeframe] = useState<'1H' | '24H' | '7D'>('24H');

  // Simulated telemetry data points (volume in $, risk score 0..1)
  const DATA = [
    { time: '00:00', volume: 1200, risk: 0.02 },
    { time: '04:00', volume: 2480, risk: 0.08 },
    { time: '08:00', volume: 4100, risk: 0.12 },
    { time: '12:00', volume: 9200, risk: 0.78 }, // Spike blocked
    { time: '16:00', volume: 6800, risk: 0.42 },
    { time: '20:00', volume: 14800, risk: 0.05 },
    { time: '24:00', volume: 19100, risk: 0.04 },
  ];

  const maxVolume = 20000;

  return (
    <div className="bg-slate-950/80 border border-white/[0.08] rounded-2xl p-6 backdrop-blur-xl h-full flex flex-col justify-between">
      
      {/* Header Bar */}
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-white/[0.08] mb-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-display font-bold text-base text-slate-100 tracking-tight flex items-center gap-2">
                LIVE OPERATIONS TELEMETRY
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              </h3>
              <span className="text-[10px] font-mono text-slate-400">
                Payment Volume ($) vs. FRAUDGUARD Anomaly Vectors
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1 bg-slate-900 border border-white/10 rounded-lg p-1">
            {(['1H', '24H', '7D'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTimeframe(t)}
                className={`px-2.5 py-1 rounded font-mono text-[10px] uppercase transition-colors ${
                  timeframe === t
                    ? 'bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Real-Time Telemetry SVG Graph Chart */}
        <div className="relative h-48 w-full mb-4">
          <svg className="w-full h-full overflow-visible" viewBox="0 0 700 180">
            <defs>
              <linearGradient id="volumeGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10B981" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#10B981" stopOpacity="0" />
              </linearGradient>
            </defs>

            {/* Background Grid Lines */}
            <line x1="0" y1="40" x2="700" y2="40" stroke="rgba(255,255,255,0.05)" strokeDasharray="4 4" />
            <line x1="0" y1="90" x2="700" y2="90" stroke="rgba(255,255,255,0.05)" strokeDasharray="4 4" />
            <line x1="0" y1="140" x2="700" y2="140" stroke="rgba(255,255,255,0.05)" strokeDasharray="4 4" />

            {/* Filled Area Chart */}
            <path
              d="M 0 160 L 0 150 Q 100 130 200 100 T 400 40 T 600 20 L 700 10 L 700 160 Z"
              fill="url(#volumeGrad)"
            />

            {/* Volume Path */}
            <path
              d="M 0 150 Q 100 130 200 100 T 400 40 T 600 20 L 700 10"
              fill="none"
              stroke="#10B981"
              strokeWidth="2.5"
              strokeLinecap="round"
            />

            {/* Risk Vector Spike Overlay Line (Red/Amber Alert at 12:00) */}
            <path
              d="M 0 160 Q 200 155 350 70 T 700 160"
              fill="none"
              stroke="#EF4444"
              strokeWidth="1.5"
              strokeDasharray="5 5"
            />

            {/* Data Point Nodes */}
            <circle cx="200" cy="100" r="4" fill="#10B981" />
            <circle cx="350" cy="70" r="5" fill="#EF4444" className="animate-pulse" />
            <circle cx="600" cy="20" r="4" fill="#10B981" />
          </svg>
        </div>
      </div>

      {/* Chart Summary Footer */}
      <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono text-slate-400">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            Payment Settlement Volume ($)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-red-400" />
            Anomaly Risk Vector Level
          </span>
        </div>
        <span className="text-emerald-400 font-bold">100% Policy Bound</span>
      </div>

    </div>
  );
}
