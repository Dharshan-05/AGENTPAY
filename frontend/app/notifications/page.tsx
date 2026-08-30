'use client';
import { useState, useMemo } from 'react';
import { AgentPayShell } from '@/components/layout/AgentPayShell';
import { PageHeader } from '@/components/layout/PageHeader';
import { AGMetricCard } from '@/components/ui/ag-card';
import { AGButton } from '@/components/ui/ag-button';
import { AGBadge } from '@/components/ui/ag-badge';
import { Bell, RefreshCw } from 'lucide-react';
import { NotificationsTabType } from '@/components/notifications/notification-types';
import { MOCK_NOTIFICATIONS } from '@/components/notifications/notification-data';

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState<NotificationsTabType>('DELIVERIES');
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    return MOCK_NOTIFICATIONS.filter(n => 
      !search || n.notificationId.toLowerCase().includes(search.toLowerCase()) || n.event.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <AgentPayShell activeTab="notifications">
      <div className="space-y-6 pb-12 font-mono text-xs">
        <PageHeader
          eyebrow="MULTI-CHANNEL ALERT & NOTIFICATION DISPATCH ENGINE"
          title="NOTIFICATION"
          highlightTitle="DISPATCH"
          description="Real-time event notification routing, webhook exponential retry backoff, Slack/SMS/Email dispatch, and delivery SLA tracking."
          icon={Bell}
          statusBadge="● NOTIFICATION DISPATCH ACTIVE"
          actions={
            <div className="flex gap-2">
              <AGButton variant="ghost" size="sm" onClick={() => alert('Telemetry refreshed.')}><RefreshCw className="w-3.5 h-3.5 mr-1.5" /> REFRESH</AGButton>
            </div>
          }
        />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <AGMetricCard label="DELIVERIES 24H" value="42,890" subtext="TOTAL DISPATCHED" accentColor="text-blue-400" />
          <AGMetricCard label="DELIVERY SLA" value="99.98%" subtext="SUCCESSFUL DISPATCH" accentColor="text-emerald-400" />
          <AGMetricCard label="AVG DISPATCH LATENCY" value="54ms" subtext="SUB-100MS LATENCY" accentColor="text-emerald-400" />
          <AGMetricCard label="FAILED DISPATCH" value="00" subtext="ZERO DEAD-LETTER DROPS" accentColor="text-emerald-400" />
        </div>
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] flex gap-3 items-center">
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search Notification ID, Event..." className="flex-1 bg-slate-950 border border-white/[0.08] rounded-xl px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none" />
          <button onClick={() => setSearch('')} className="px-3 py-2 rounded-xl border border-white/[0.08] text-slate-400">RESET</button>
        </div>
        <div className="flex gap-2 border-b border-white/[0.08] pb-3">
          {(['DELIVERIES', 'WEBHOOK_RETRIES', 'EMAIL', 'SMS', 'FAILURE_ALERTS', 'TEMPLATES', 'AUDIT'] as NotificationsTabType[]).map(t => (
            <button key={t} onClick={() => setActiveTab(t)} className={`px-3 py-1.5 rounded-xl font-bold ${activeTab === t ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-slate-400'}`}>{t}</button>
          ))}
        </div>
        {activeTab === 'DELIVERIES' && (
          <div className="p-4 rounded-2xl bg-slate-900/60 border border-white/[0.08] overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/[0.08] text-[10px] text-slate-500 uppercase">
                  <th className="p-3">NOTIFICATION ID</th>
                  <th className="p-3">EVENT</th>
                  <th className="p-3">CHANNEL</th>
                  <th className="p-3">TARGET</th>
                  <th className="p-3">LATENCY</th>
                  <th className="p-3">TIMESTAMP</th>
                  <th className="p-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.04]">
                {filtered.map(n => (
                  <tr key={n.id} className="hover:bg-slate-900/40 cursor-pointer">
                    <td className="p-3 font-bold text-blue-400">{n.notificationId}</td>
                    <td className="p-3 font-bold text-slate-200">{n.event}</td>
                    <td className="p-3 font-bold text-purple-400">{n.channel}</td>
                    <td className="p-3 text-slate-300">{n.target}</td>
                    <td className="p-3 text-emerald-400 font-bold">{n.latencyMs}ms</td>
                    <td className="p-3 text-slate-500">{n.timestamp}</td>
                    <td className="p-3"><AGBadge status={n.status} size="sm" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {activeTab !== 'DELIVERIES' && <div className="p-8 rounded-2xl bg-slate-900/60 border border-white/[0.08] text-center text-slate-400">{activeTab} OPERATIONAL VIEW ACTIVE</div>}
      </div>
    </AgentPayShell>
  );
}
