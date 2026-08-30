'use client';

import { SourceAgentRecord, SourceMerchantRecord, SourceAnomalyRecord } from './source-types';
import { Users, ShoppingBag, AlertTriangle } from 'lucide-react';

interface SourceTablesProps {
  agents: SourceAgentRecord[];
  merchants: SourceMerchantRecord[];
  anomalies: SourceAnomalyRecord[];
  onSelectRow: (item: any) => void;
}

export function SourceTables({ agents, merchants, anomalies, onSelectRow }: SourceTablesProps) {
  return (
    <div className="space-y-6 font-sans text-slate-800">
      
      {/* AGENT PERFORMANCE TABLE */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex justify-between items-center pb-3 border-b border-slate-100">
          <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
            <Users className="w-4 h-4 text-blue-600" />
            Agent Performance Matrix
          </h3>
          <span className="text-xs text-slate-500">Click row for Inspector Drill-Down</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
                <th className="p-3">Agent</th>
                <th className="p-3">Transactions</th>
                <th className="p-3">Success Rate</th>
                <th className="p-3">Avg Risk</th>
                <th className="p-3">Violations</th>
                <th className="p-3">Total Value</th>
                <th className="p-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {agents.map((a) => (
                <tr
                  key={a.id}
                  onClick={() => onSelectRow(a)}
                  className="hover:bg-blue-50/50 cursor-pointer transition-colors"
                >
                  <td className="p-3 font-bold text-slate-900 font-sans">
                    {a.name} <span className="text-slate-400 text-[10px] font-mono">({a.agentId})</span>
                  </td>
                  <td className="p-3 text-slate-700 font-bold">{a.transactions}</td>
                  <td className="p-3 text-emerald-600 font-bold">{a.successRate}</td>
                  <td className="p-3 text-amber-600 font-bold">{a.avgRisk}</td>
                  <td className="p-3 text-slate-600">{a.policyViolations}</td>
                  <td className="p-3 text-slate-900 font-bold">{a.totalValue}</td>
                  <td className="p-3 text-right font-sans">
                    <span
                      className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        a.status === 'AUTHORIZED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {a.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* TWO COLUMNS: MERCHANTS & ANOMALIES */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Merchant Category */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <ShoppingBag className="w-4 h-4 text-emerald-600" />
              Merchant & Category Analytics
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse font-mono">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 bg-slate-50 uppercase text-[10px]">
                  <th className="p-2.5">Merchant</th>
                  <th className="p-2.5">Category</th>
                  <th className="p-2.5">Volume</th>
                  <th className="p-2.5 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {merchants.map((m) => (
                  <tr key={m.name} className="hover:bg-slate-50">
                    <td className="p-2.5 font-bold text-slate-900 font-sans">{m.name}</td>
                    <td className="p-2.5 text-slate-500 font-sans">{m.category}</td>
                    <td className="p-2.5 text-emerald-600 font-bold">{m.volume}</td>
                    <td className="p-2.5 text-right font-sans">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                          m.status === 'AUTHORIZED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {m.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Anomaly Stream */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex justify-between items-center pb-3 border-b border-slate-100">
            <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              Anomaly Detection Stream
            </h3>
          </div>

          <div className="space-y-2 text-xs">
            {anomalies.map((an) => (
              <div key={an.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex justify-between items-center">
                <div>
                  <span className="font-bold text-slate-900 block">{an.title}</span>
                  <span className="text-slate-500 text-[10px] font-mono">{an.agent} ({an.agentId}) · {an.timestamp}</span>
                </div>
                <span className="px-2.5 py-1 bg-rose-100 text-rose-800 font-bold text-[10px] rounded-full">
                  {an.severity}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
