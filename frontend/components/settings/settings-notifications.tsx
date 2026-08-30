'use client';

import { AGCard } from '@/components/ui/ag-card';
import { AGBadge } from '@/components/ui/ag-badge';
import { Bell, Check } from 'lucide-react';
import { useState } from 'react';

export function SettingsNotifications() {
  const [securityAlerts, setSecurityAlerts] = useState({ email: true, inApp: true, webhook: true });
  const [paymentAlerts, setPaymentAlerts] = useState({ email: true, inApp: true, webhook: false });
  const [agentAlerts, setAgentAlerts] = useState({ email: true, inApp: true, webhook: true });
  const [fraudAlerts, setFraudAlerts] = useState({ email: true, inApp: true, webhook: true });

  return (
    <AGCard className="space-y-4 font-mono text-xs max-w-4xl">
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Bell className="w-5 h-5 text-blue-400" /> NOTIFICATION PREFERENCES & ROUTING
          </h3>
          <p className="text-[10px] text-slate-400">Configure real-time delivery channels for security and operational events</p>
        </div>
        <AGBadge status="POLICY_SECURE" label="CHANNELS ACTIVE" />
      </div>

      <div className="space-y-3">
        {[
          { label: 'Security & Auth Alerts (Critical)', state: securityAlerts, setState: setSecurityAlerts, required: true },
          { label: 'Payment Execution & Settlement Events', state: paymentAlerts, setState: setPaymentAlerts, required: false },
          { label: 'AgentGuard Policy Interventions', state: agentAlerts, setState: setAgentAlerts, required: false },
          { label: 'FraudGuard Risk Escalations', state: fraudAlerts, setState: setFraudAlerts, required: false },
        ].map((item, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2">
            <div className="flex justify-between items-center">
              <span className="font-bold text-slate-100 text-xs">{item.label}</span>
              {item.required && <span className="text-[10px] text-emerald-400 font-bold">MANDATORY</span>}
            </div>

            <div className="flex items-center gap-4 text-[10px]">
              {(['email', 'inApp', 'webhook'] as const).map((channel) => {
                const isChecked = item.state[channel];
                return (
                  <button
                    key={channel}
                    disabled={item.required && channel !== 'webhook'}
                    onClick={() =>
                      item.setState((prev) => ({ ...prev, [channel]: !prev[channel] }))
                    }
                    className={`px-3 py-1.5 rounded-lg border font-bold flex items-center gap-1.5 transition-all ${
                      isChecked
                        ? 'bg-blue-500/10 border-blue-500/30 text-blue-400'
                        : 'bg-slate-900 border-white/[0.04] text-slate-500'
                    }`}
                  >
                    <span className="uppercase">{channel}</span>
                    {isChecked && <Check className="w-3 h-3 text-blue-400" />}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </AGCard>
  );
}
