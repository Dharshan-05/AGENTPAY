'use client';

interface SourceMetricsProps {
  endpointsCount: number;
  activeCount: number;
  deliveries24h: string;
  successRate: string;
  p95Latency: string;
  failedRetryingCount: number;
}

export function SourceMetrics({
  endpointsCount,
  activeCount,
  deliveries24h,
  successRate,
  p95Latency,
  failedRetryingCount,
}: SourceMetricsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 font-sans">
      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="text-[10px] font-mono text-slate-400 uppercase font-semibold">WEBHOOK ENDPOINTS</div>
        <div className="text-2xl font-bold text-slate-900 mt-1">{endpointsCount} TOTAL</div>
        <div className="text-[11px] text-emerald-600 font-medium mt-1">{activeCount} ACTIVE &amp; HEALTHY</div>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="text-[10px] font-mono text-slate-400 uppercase font-semibold">DELIVERIES 24H</div>
        <div className="text-2xl font-bold text-slate-900 mt-1">{deliveries24h}</div>
        <div className="text-[11px] text-emerald-600 font-medium mt-1">+14.2% Volume</div>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="text-[10px] font-mono text-slate-400 uppercase font-semibold">SUCCESS RATE</div>
        <div className="text-2xl font-bold text-emerald-600 mt-1">{successRate}</div>
        <div className="text-[11px] text-slate-500 font-mono mt-1">SLA &gt; 99.90%</div>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="text-[10px] font-mono text-slate-400 uppercase font-semibold">P95 LATENCY</div>
        <div className="text-2xl font-bold text-blue-600 mt-1">{p95Latency}</div>
        <div className="text-[11px] text-slate-500 font-mono mt-1">HTTP ROUTE AVG</div>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="text-[10px] font-mono text-slate-400 uppercase font-semibold">FAILED / RETRYING</div>
        <div className="text-2xl font-bold text-amber-600 mt-1">{failedRetryingCount} QUEUED</div>
        <div className="text-[11px] text-amber-600 font-medium mt-1">EXPONENTIAL BACKOFF</div>
      </div>

      <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm">
        <div className="text-[10px] font-mono text-slate-400 uppercase font-semibold">DEAD-LETTER QUEUE</div>
        <div className="text-2xl font-bold text-rose-600 mt-1">1 EXHAUSTED</div>
        <div className="text-[11px] text-slate-500 font-mono mt-1">MANUAL REPLAY REQ</div>
      </div>
    </div>
  );
}
