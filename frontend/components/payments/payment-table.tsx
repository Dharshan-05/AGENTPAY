'use client';

import { PaymentRecord } from './types';
import { PaymentStatusBadge } from './payment-status';
import { AGButton } from '@/components/ui/ag-button';
import { CreditCard } from 'lucide-react';

interface PaymentTableProps {
  payments: PaymentRecord[];
  selectedPaymentId: string | null;
  onSelectPayment: (id: string) => void;
}

export function PaymentTable({ payments, selectedPaymentId, onSelectPayment }: PaymentTableProps) {
  return (
    <div className="rounded-2xl border border-white/[0.08] bg-slate-900/60 overflow-hidden backdrop-blur-xl font-mono text-xs shadow-2xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/[0.08] bg-slate-950/80 text-slate-400 text-[10px] uppercase tracking-wider">
              <th className="p-3.5">Status</th>
              <th className="p-3.5">Payment ID</th>
              <th className="p-3.5">Amount</th>
              <th className="p-3.5">Method</th>
              <th className="p-3.5">Customer</th>
              <th className="p-3.5">Merchant / Description</th>
              <th className="p-3.5">Created</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.04]">
            {payments.length === 0 ? (
              <tr>
                <td colSpan={8} className="p-8 text-center text-slate-500">
                  No payment transactions found matching the selected filter criteria.
                </td>
              </tr>
            ) : (
              payments.map((p) => {
                const isSelected = selectedPaymentId === p.id;
                return (
                  <tr
                    key={p.id}
                    onClick={() => onSelectPayment(p.id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-emerald-500/10 border-l-2 border-l-emerald-400'
                        : 'hover:bg-slate-800/40'
                    }`}
                  >
                    <td className="p-3.5">
                      <PaymentStatusBadge status={p.status} />
                    </td>

                    <td className="p-3.5 font-bold text-slate-100">{p.id}</td>

                    <td className="p-3.5 font-bold text-emerald-400">{p.amount}</td>

                    <td className="p-3.5 text-slate-300 font-semibold">{p.method}</td>

                    <td className="p-3.5 text-slate-300">
                      <div className="font-bold text-slate-200">{p.customerName}</div>
                      <div className="text-[10px] text-slate-500">{p.customerEmail}</div>
                    </td>

                    <td className="p-3.5 text-slate-300 max-w-xs truncate">
                      <div className="text-slate-200 font-semibold">{p.merchant}</div>
                      <div className="text-[10px] text-slate-500 truncate">{p.description}</div>
                    </td>

                    <td className="p-3.5 text-slate-400 text-[10px]">{p.timestamp}</td>

                    <td className="p-3.5 text-right">
                      <AGButton variant="ghost" size="sm">
                        Inspect
                      </AGButton>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
