'use client';

import { Bell, Check } from 'lucide-react';
import { useState } from 'react';

export function SourceNotifications() {
  const [securityAlerts, setSecurityAlerts] = useState(true);
  const [paymentAlerts, setPaymentAlerts] = useState(true);
  const [agentAlerts, setAgentAlerts] = useState(true);
  const [fraudAlerts, setFraudAlerts] = useState(true);

  return (
    <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-slate-800">
      <div className="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Bell className="w-4 h-4 text-blue-600" />
            Notification Preferences & Channels
          </h3>
          <p className="text-xs text-slate-500">Excavated notification routing matrix</p>
        </div>
      </div>

      <div className="space-y-3 text-xs font-sans">
        {[
          { label: 'Security & Auth Alerts (Critical)', state: securityAlerts, setState: setSecurityAlerts, required: true },
          { label: 'Payment Execution & Settlement Alerts', state: paymentAlerts, setState: setPaymentAlerts, required: false },
          { label: 'Agent Policy Interventions', state: agentAlerts, setState: setAgentAlerts, required: false },
          { label: 'FraudGuard Risk Escalations', state: fraudAlerts, setState: setFraudAlerts, required: false },
        ].map((item, idx) => (
          <div key={idx} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <span className="font-bold text-slate-900 block">{item.label}</span>
              <span className="text-slate-500 text-[11px]">Email + In-App + Webhook channels</span>
            </div>

            <button
              disabled={item.required}
              onClick={() => item.setState(!item.state)}
              className={`px-3 py-1.5 rounded-xl font-bold text-xs transition-colors ${
                item.state ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'
              }`}
            >
              {item.state ? 'ENABLED' : 'DISABLED'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
