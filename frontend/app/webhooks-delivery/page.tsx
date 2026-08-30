'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Radio, RefreshCw } from 'lucide-react';
import { WebhooksDeliveryTabType } from '@/components/webhooks-delivery/webhooks-delivery-types';
import { MOCK_WEBHOOKS_DELIVERY } from '@/components/webhooks-delivery/webhooks-delivery-data';

export default function WebhooksDeliveryPage() {
  const [activeTab, setActiveTab] = useState<WebhooksDeliveryTabType>('DISPATCH_LOGS');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_WEBHOOKS_DELIVERY.filter(w => 
      !search || w.webhookId.toLowerCase().includes(search.toLowerCase()) || w.eventType.toLowerCase().includes(search.toLowerCase()) || w.targetEndpoint.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="webhooks-delivery">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="WEBHOOK EVENT DISPATCH & EXPONENTIAL BACKOFF RETRY PLANE"
          title="WEBHOOK"
          highlightTitle="DISPATCH & DELIVERY"
          description="Autonomous webhook event dispatching, HMAC-SHA256 signature verification, exponential backoff retries, and endpoint SLA monitoring."
          icon={Radio}
          statusBadge="● WEBHOOK DISPATCH ENGINE LIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="DISPATCHED EVENTS" value={`${MOCK_WEBHOOKS_DELIVERY.length}`} subtext="DELIVERED 24H" accentColor="text-blue-400" />
          <AGMetricCard label="DELIVERY RATE" value="99.98%" subtext="HIGH SUCCESS RATE" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG DISPATCH SLA" value="115ms" subtext="REAL-TIME DELIVERY" accentColor="text-emerald-400" />
          <AGMetricCard label="HMAC SIGNATURE" value="SHA256 VERIFIED" subtext="SECURE EVENT PAYLOAD" accentColor="text-purple-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Webhook ID, Event Type, Endpoint..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['DISPATCH_LOGS', 'RETRY_QUEUE', 'HMAC_SIGNATURES', 'ENDPOINT_HEALTH', 'AUDIT'] as WebhooksDeliveryTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'DISPATCH_LOGS' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">WEBHOOK ID</th>
                  <th className="p-3">EVENT TYPE</th>
                  <th className="p-3">TARGET ENDPOINT</th>
                  <th className="p-3">HTTP STATUS</th>
                  <th className="p-3">ATTEMPT</th>
                  <th className="p-3">LATENCY</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(w => (
                  <tr key={w.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{w.webhookId}</td>
                    <td className="p-3 font-bold text-purple-400 font-mono">{w.eventType}</td>
                    <td className="p-3 text-slate-300 font-mono truncate max-w-[200px]">{w.targetEndpoint}</td>
                    <td className="p-3 font-bold text-emerald-400">{w.httpStatus}</td>
                    <td className="p-3 text-slate-400">{w.attemptCount}</td>
                    <td className="p-3 text-emerald-400 font-mono">{w.latencyMs} ms</td>
                    <td className="p-3"><AGBadge status={w.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'DISPATCH_LOGS' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
