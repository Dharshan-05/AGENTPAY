'use client';

import { AGButton } from '@/components/ui/ag-button';
import { Search, Filter, RotateCcw } from 'lucide-react';

interface ReconciliationControlsProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedProcessor: string;
  onProcessorChange: (proc: string) => void;
  selectedStatus: string;
  onStatusChange: (st: string) => void;
  selectedDateRange: string;
  onDateRangeChange: (d: string) => void;
  onReset: () => void;
}

export function ReconciliationControls({
  searchQuery,
  onSearchChange,
  selectedProcessor,
  onProcessorChange,
  selectedStatus,
  onStatusChange,
  selectedDateRange,
  onDateRangeChange,
  onReset,
}: ReconciliationControlsProps) {
  return (
    <div className="p-4 rounded-2xl border border-white/[0.08] bg-slate-900/60 backdrop-blur-xl space-y-3 font-mono text-xs shadow-2xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* SEARCH FIELD */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search batch ID, transaction ID, dispute ID, agent..."
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        {/* PROCESSOR SELECTOR */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">PROCESSOR:</span>
          <select
            value={selectedProcessor}
            onChange={(e) => onProcessorChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">ALL PROCESSORS</option>
            <option value="Stripe">STRIPE</option>
            <option value="Adyen">ADYEN</option>
            <option value="Visa Direct">VISA DIRECT</option>
          </select>
        </div>

        {/* STATUS SELECTOR */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">STATUS:</span>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">ALL STATUSES</option>
            <option value="MATCHED">MATCHED</option>
            <option value="VARIANCE">VARIANCE</option>
            <option value="REVIEW">REVIEW</option>
            <option value="FAILED">FAILED</option>
          </select>
        </div>

        {/* DATE RANGE */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-slate-400 uppercase font-bold">RANGE:</span>
          <select
            value={selectedDateRange}
            onChange={(e) => onDateRangeChange(e.target.value)}
            className="px-2.5 py-1.5 bg-slate-950 border border-white/10 rounded-xl text-xs text-slate-200 font-bold focus:outline-none focus:border-blue-500/50"
          >
            <option value="24H">LAST 24 HOURS</option>
            <option value="7D">LAST 7 DAYS</option>
            <option value="30D">LAST 30 DAYS</option>
            <option value="90D">LAST 90 DAYS</option>
          </select>
        </div>

        {/* RESET BUTTON */}
        <AGButton variant="ghost" size="sm" icon={RotateCcw} onClick={onReset}>
          RESET
        </AGButton>
      </div>
    </div>
  );
}
