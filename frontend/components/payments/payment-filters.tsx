'use client';

import { Search, Filter, RotateCcw } from 'lucide-react';
import { AGButton } from '@/components/ui/ag-button';

interface PaymentFiltersProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  statusFilter: string;
  onStatusChange: (status: string) => void;
  methodFilter: string;
  onMethodChange: (method: string) => void;
  dateFilter: string;
  onDateChange: (date: string) => void;
  onReset: () => void;
}

export function PaymentFilters({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusChange,
  methodFilter,
  onMethodChange,
  dateFilter,
  onDateChange,
  onReset,
}: PaymentFiltersProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] backdrop-blur-xl font-mono text-xs">
      
      {/* Search Input */}
      <div className="relative flex-1 min-w-[240px]">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search payment ID, customer, merchant..."
          className="w-full pl-10 pr-4 py-2 bg-slate-950/80 border border-white/10 rounded-xl text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/50 transition-colors"
        />
      </div>

      {/* Filter Selects */}
      <div className="flex flex-wrap items-center gap-2">
        <select
          value={statusFilter}
          onChange={(e) => onStatusChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="ALL">Status: All</option>
          <option value="PAID">PAID / CAPTURED</option>
          <option value="SETTLED">SETTLED</option>
          <option value="AUTHORIZED">AUTHORIZED</option>
          <option value="PENDING">PENDING</option>
          <option value="PROCESSING">PROCESSING</option>
          <option value="FAILED">FAILED / DECLINED</option>
          <option value="REFUNDED">REFUNDED</option>
        </select>

        <select
          value={methodFilter}
          onChange={(e) => onMethodChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="ALL">Method: All</option>
          <option value="VISA">Visa</option>
          <option value="MASTERCARD">Mastercard</option>
          <option value="GCASH">GCash</option>
          <option value="MAYA">Maya</option>
          <option value="WIRE">Wire Transfer</option>
        </select>

        <select
          value={dateFilter}
          onChange={(e) => onDateChange(e.target.value)}
          className="bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500/50"
        >
          <option value="24H">Date: 24H</option>
          <option value="7D">Date: 7 Days</option>
          <option value="30D">Date: 30 Days</option>
        </select>

        <AGButton variant="ghost" size="sm" icon={RotateCcw} onClick={onReset}>
          Reset
        </AGButton>
      </div>

    </div>
  );
}
