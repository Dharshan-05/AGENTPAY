'use client';

import { AGButton } from '@/components/ui/ag-button';
import { Filter, RotateCcw } from 'lucide-react';

interface AnalyticsControlsProps {
  dateRange: string;
  onDateRangeChange: (r: string) => void;
  selectedAgent: string;
  onAgentChange: (a: string) => void;
  statusFilter: string;
  onStatusChange: (s: string) => void;
  riskBand: string;
  onRiskBandChange: (r: string) => void;
  merchantFilter: string;
  onMerchantChange: (m: string) => void;
  regionFilter: string;
  onRegionChange: (reg: string) => void;
  onReset: () => void;
}

export function AnalyticsControls({
  dateRange,
  onDateRangeChange,
  selectedAgent,
  onAgentChange,
  statusFilter,
  onStatusChange,
  riskBand,
  onRiskBandChange,
  merchantFilter,
  onMerchantChange,
  regionFilter,
  onRegionChange,
  onReset,
}: AnalyticsControlsProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs">
      <div className="flex flex-wrap items-center gap-2">
        {/* Date Range Selector */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-white/10 text-[11px]">
          {['24H', '7D', '30D', '90D', 'CUSTOM'].map((r) => (
            <button
              key={r}
              onClick={() => onDateRangeChange(r)}
              className={`px-2.5 py-1 rounded-lg font-bold transition-all ${
                dateRange === r
                  ? 'bg-emerald-500 text-slate-950 shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        {/* Agent Filter */}
        <select
          value={selectedAgent}
          onChange={(e) => onAgentChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="ALL">Agent: All Agents</option>
          <option value="AGT-892">Procurement Agent #892</option>
          <option value="AGT-441">Shopping Agent #441</option>
          <option value="AGT-118">Travel Agent #118</option>
          <option value="AGT-203">Logistics Agent #203</option>
        </select>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => onStatusChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="ALL">Status: All</option>
          <option value="AUTHORIZED">AUTHORIZED</option>
          <option value="CAPTURED">CAPTURED</option>
          <option value="FAILED">FAILED</option>
          <option value="REFUNDED">REFUNDED</option>
        </select>

        {/* Risk Band Filter */}
        <select
          value={riskBand}
          onChange={(e) => onRiskBandChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="ALL">Risk: All Bands</option>
          <option value="LOW">LOW RISK</option>
          <option value="MEDIUM">MEDIUM RISK</option>
          <option value="HIGH">HIGH RISK</option>
          <option value="CRITICAL">CRITICAL RISK</option>
        </select>

        {/* Merchant Filter */}
        <select
          value={merchantFilter}
          onChange={(e) => onMerchantChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="ALL">Merchant: All</option>
          <option value="Acme Hardware">Acme Hardware</option>
          <option value="ElectroHub">ElectroHub</option>
          <option value="United Airlines">United Airlines</option>
        </select>

        {/* Region Filter */}
        <select
          value={regionFilter}
          onChange={(e) => onRegionChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="ALL">Region: All</option>
          <option value="US">North America (US)</option>
          <option value="EU">Europe (EU)</option>
          <option value="APAC">Asia-Pacific (APAC)</option>
          <option value="INDIA">India (IN)</option>
          <option value="MIDDLE_EAST">Middle East (ME)</option>
        </select>
      </div>

      <AGButton variant="ghost" size="sm" icon={RotateCcw} onClick={onReset}>
        Reset Filters
      </AGButton>
    </div>
  );
}
