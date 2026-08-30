'use client';

import { PaymentInstrumentRecord } from './source-types';
import { AGBadge } from '@/components/ui/ag-badge';
import { CreditCard, Landmark } from 'lucide-react';

interface SourceCardsBanksProps {
  instruments: PaymentInstrumentRecord[];
  onSelect: (item: PaymentInstrumentRecord) => void;
}

export function SourceCardsBanks({ instruments, onSelect }: SourceCardsBanksProps) {
  const cardsAndBanks = instruments.filter(
    i => i.type === 'CARD' || i.type === 'VIRTUAL_CARD' || i.type === 'BANK_ACCOUNT' || i.type === 'BANK_TRANSFER' || i.type === 'TOKENIZED_CARD'
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 font-mono text-xs">
      {cardsAndBanks.map((item) => {
        const isBank = item.type === 'BANK_ACCOUNT' || item.type === 'BANK_TRANSFER';
        return (
          <div
            key={item.id}
            onClick={() => onSelect(item)}
            className="p-5 rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950/80 border border-white/[0.08] backdrop-blur-xl space-y-4 hover:border-blue-500/40 transition-all cursor-pointer group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400">
                  {isBank ? <Landmark className="w-4 h-4" /> : <CreditCard className="w-4 h-4" />}
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
                <span className="text-slate-500 block">ASSIGNED AGENT</span>
                <span className="font-bold text-blue-400">{item.agentId}</span>
              </div>
              <div>
                <span className="text-slate-500 block">SPEND LIMIT</span>
                <span className="font-bold text-emerald-400">{item.spendLimit}</span>
              </div>
              <div>
                <span className="text-slate-500 block">PROCESSOR</span>
                <span className="text-slate-300">{item.processor}</span>
              </div>
              <div>
                <span className="text-slate-500 block">RISK TIER</span>
                <span className={item.riskTier === 'LOW' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>{item.riskTier} ({item.riskScore}/100)</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
