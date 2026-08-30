'use client';

interface SourceControlsProps {
  searchQuery: string;
  onSearchChange: (v: string) => void;
  selectedStatus: string;
  onStatusChange: (v: string) => void;
  selectedEventType: string;
  onEventTypeChange: (v: string) => void;
  selectedEnvironment: string;
  onEnvironmentChange: (v: string) => void;
  selectedHttpStatus: string;
  onHttpStatusChange: (v: string) => void;
  selectedEndpoint: string;
  onEndpointChange: (v: string) => void;
  onReset: () => void;
}

export function SourceControls({
  searchQuery,
  onSearchChange,
  selectedStatus,
  onStatusChange,
  selectedEventType,
  onEventTypeChange,
  selectedEnvironment,
  onEnvironmentChange,
  selectedHttpStatus,
  onHttpStatusChange,
  selectedEndpoint,
  onEndpointChange,
  onReset,
}: SourceControlsProps) {
  return (
    <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm font-sans">
      <div className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[200px]">
          <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
            SEARCH WEBHOOKS &amp; EVENTS
          </label>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search Event ID, Delivery ID, URL, Agent ID..."
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono text-slate-800 placeholder-slate-400 focus:bg-white focus:border-purple-500 focus:outline-none transition-colors"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">STATUS</label>
          <select
            value={selectedStatus}
            onChange={(e) => onStatusChange(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono text-slate-700 focus:bg-white focus:border-purple-500 focus:outline-none"
          >
            <option value="ALL">ALL STATUSES</option>
            <option value="DELIVERED">DELIVERED</option>
            <option value="FAILED">FAILED</option>
            <option value="RETRYING">RETRYING</option>
            <option value="EXHAUSTED">EXHAUSTED</option>
            <option value="HEALTHY">HEALTHY</option>
            <option value="DEGRADED">DEGRADED</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">EVENT TYPE</label>
          <select
            value={selectedEventType}
            onChange={(e) => onEventTypeChange(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono text-slate-700 focus:bg-white focus:border-purple-500 focus:outline-none"
          >
            <option value="ALL">ALL EVENTS</option>
            <option value="transaction.captured">transaction.captured</option>
            <option value="policy.blocked">policy.blocked</option>
            <option value="risk.alerted">risk.alerted</option>
            <option value="refund.succeeded">refund.succeeded</option>
            <option value="agent.suspended">agent.suspended</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">ENDPOINT</label>
          <select
            value={selectedEndpoint}
            onChange={(e) => onEndpointChange(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono text-slate-700 focus:bg-white focus:border-purple-500 focus:outline-none"
          >
            <option value="ALL">ALL ENDPOINTS</option>
            <option value="WHK-001">WHK-001 (Finance Gateway)</option>
            <option value="WHK-002">WHK-002 (Fraud Monitor)</option>
            <option value="WHK-003">WHK-003 (ERP NetSuite)</option>
            <option value="WHK-004">WHK-004 (Sandbox Test)</option>
            <option value="WHK-005">WHK-005 (Legacy Accounting)</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">ENV</label>
          <select
            value={selectedEnvironment}
            onChange={(e) => onEnvironmentChange(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono text-slate-700 focus:bg-white focus:border-purple-500 focus:outline-none"
          >
            <option value="ALL">ALL ENV</option>
            <option value="PRODUCTION">PRODUCTION</option>
            <option value="STAGING">STAGING</option>
            <option value="SANDBOX">SANDBOX</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">HTTP CODE</label>
          <select
            value={selectedHttpStatus}
            onChange={(e) => onHttpStatusChange(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono text-slate-700 focus:bg-white focus:border-purple-500 focus:outline-none"
          >
            <option value="ALL">ALL HTTP</option>
            <option value="200">200 OK</option>
            <option value="504">504 TIMEOUT</option>
            <option value="503">503 UNAVAILABLE</option>
          </select>
        </div>

        <button
          onClick={onReset}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 font-mono text-xs font-semibold rounded-xl border border-slate-200 transition-colors"
        >
          RESET
        </button>
      </div>
    </div>
  );
}
