'use client';

import { PaymentInstrumentRecord } from './payment-method-types';
import { AGBadge } from '@/components/ui/ag-badge';
import { CreditCard, Landmark } from 'lucide-react';

interface PaymentMethodCardsBanksProps {
  instruments: PaymentInstrumentRecord[];
  onSelect: (item: PaymentInstrumentRecord) => void;
}

export function PaymentMethodCardsBanks({ instruments, onSelect }: PaymentMethodCardsBanksProps) {
  const cards = instruments.filter(i => i.type.includes('CARD') || i.type === 'WALLET');
  const banks = instruments.filter(i => i.type.includes('BANK') || i.type === 'UPI');

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* CARD INSTRUMENTS */}
      <div className="space-y-3">
        <h3 className="font-bold text-slate-200 text-xs flex items-center gap-2">
          <CreditCard className="w-3.5 h-3.5 text-blue-400" /> CARD INSTRUMENTS
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cards.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelect(item)}
              className="p-5 rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950/80 border border-white/[0.08] backdrop-blur-xl space-y-4 hover:border-blue-500/40 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400">
                    <CreditCard className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-purple-400 font-bold uppercase block">{item.type}</span>
                    <span className="font-bold text-slate-100 text-sm group-hover:text-blue-300">{item.name}</span>
                  </div>
                </div>
                <AGBadge status={item.status} size="sm" />
              </div>

              <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.04] space-y-1">
                <div className="text-[9px] text-slate-500 uppercase">MASKED IDENTIFIER</div>
                <div className="text-base font-bold font-mono text-slate-100 tracking-wider">{item.maskedIdentifier}</div>
                <div className="text-[10px] text-slate-400">{item.brandOrBank} · Exp {item.expirationDate}</div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div>
                  <span className="text-slate-500 block">3DS STATUS</span>
                  <span className="font-bold text-emerald-400">{item.threeDsStatus}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">AVS / CVV</span>
                  <span className="font-bold text-emerald-400">{item.avsCvvResult}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* BANK INSTRUMENTS */}
      <div className="space-y-3">
        <h3 className="font-bold text-slate-200 text-xs flex items-center gap-2">
          <Landmark className="w-4 h-4 text-emerald-400" /> BANK &amp; DIRECT DEBIT INSTRUMENTS
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {banks.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelect(item)}
              className="p-5 rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950/80 border border-white/[0.08] backdrop-blur-xl space-y-4 hover:border-emerald-500/40 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                    <Landmark className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] text-purple-400 font-bold uppercase block">{item.type}</span>
                    <span className="font-bold text-slate-100 text-sm group-hover:text-emerald-300">{item.name}</span>
                  </div>
                </div>
                <AGBadge status={item.status} size="sm" />
              </div>

              <div className="p-3 rounded-xl bg-slate-950/80 border border-white/[0.04] space-y-1">
                <div className="text-[9px] text-slate-500 uppercase">MASKED ACCOUNT IDENTIFIER</div>
                <div className="text-base font-bold font-mono text-slate-100 tracking-wider">{item.maskedIdentifier}</div>
                <div className="text-[10px] text-slate-400">{item.brandOrBank}</div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <div>
                  <span className="text-slate-500 block">TOKEN STATUS</span>
                  <span className="font-bold text-blue-400">{item.tokenStatus}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">PROCESSOR</span>
                  <span className="font-bold text-slate-300">{item.processor}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
