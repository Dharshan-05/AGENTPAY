'use client';

import { useEffect } from 'react';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGBadge } from '@/components/ui/ag-badge';
import { AGButton } from '@/components/ui/ag-button';
import {
  CreditCard, ShieldCheck, Activity, Lock, ArrowRight, Bot, AlertTriangle
} from 'lucide-react';
import { PaymentInstrumentRecord } from './source-types';

interface SourceInspectorProps {
  item: PaymentInstrumentRecord | null;
  onClose: () => void;
}

export function SourceInspector({ item, onClose }: SourceInspectorProps) {
  useEffect(() => {
    if (!item) return;
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [item, onClose]);

  if (!item) return null;

  return (
    <AGDrawer
      isOpen={!!item}
      onClose={onClose}
      title={`METHOD INSPECTOR: ${item.instrumentId}`}
      subtitle="PAYMENT METHOD & INSTRUMENT CONTROL"
      footer={
        <div className="space-y-2 font-mono">
          <div className="flex gap-2">
            <AGButton variant="ghost" size="sm" onClick={() => {
              navigator.clipboard?.writeText(item.instrumentId);
              alert(`Copied Instrument ID: ${item.instrumentId}`);
            }} className="flex-1">
              COPY PM ID
            </AGButton>
            <AGButton variant="ghost" size="sm" onClick={() => {
              navigator.clipboard?.writeText(item.tokenId);
              alert(`Copied Token ID: ${item.tokenId}`);
            }} className="flex-1">
              COPY TOKEN ID
            </AGButton>
          </div>
          <AGButton variant="secondary" size="md" onClick={onClose} className="w-full">
            CLOSE INSPECTOR
          </AGButton>
        </div>
      }
    >
      <div className="space-y-5 font-mono text-xs">

        {/* CAUSAL CHAIN */}
        <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-2">
          <div className="text-[9px] text-blue-400 font-bold uppercase tracking-[0.2em] mb-3">AGENTPAY CAUSAL INSTRUMENT TRACE</div>
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 flex-wrap">
            <span className="font-bold text-blue-400">{item.agentId}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className="font-bold text-purple-400">{item.policyId}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className="font-bold text-slate-200">{item.instrumentId}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className={`font-bold ${item.riskTier === 'LOW' ? 'text-emerald-400' : 'text-amber-400'}`}>RISK {item.riskScore}/100</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className="font-bold text-emerald-400">{item.processor}</span>
            <ArrowRight className="w-2.5 h-2.5 text-slate-600" />
            <span className="font-bold text-blue-300">TXN-AGP-91F2</span>
          </div>
        </div>

        {/* SECTION 01: IDENTITY */}
        <InspectorSection title="01 — METHOD IDENTITY" icon={CreditCard} color="text-blue-400">
          <Row label="Instrument ID" value={item.instrumentId} valueClass="text-blue-400 font-bold" />
          <Row label="Method Type" value={item.type} valueClass="text-purple-400 font-bold" />
          <Row label="Display Name" value={item.name} valueClass="text-slate-200 font-bold" />
          <Row label="Masked Identifier" value={item.maskedIdentifier} valueClass="text-emerald-400 font-bold" />
          <Row label="Brand / Issuer" value={item.brandOrBank} valueClass="text-slate-300" />
          <Row label="Environment" value={item.environment} valueClass={item.environment === 'PRODUCTION' ? 'text-emerald-400' : 'text-amber-400'} />
          <Row label="Status" value={item.status} valueClass={item.status === 'ACTIVE' || item.status === 'VERIFIED' ? 'text-emerald-400' : 'text-amber-400'} />
        </InspectorSection>

        {/* SECTION 02: OWNER & AGENT */}
        <InspectorSection title="02 — AGENT & GOVERNANCE" icon={Bot} color="text-purple-400">
          <Row label="Agent ID" value={item.agentId} valueClass="text-blue-400 font-bold" />
          <Row label="Agent Name" value={item.agentName} valueClass="text-slate-200" />
          <Row label="Owner / Department" value={item.owner} valueClass="text-slate-300" />
          <Row label="Bound Policy ID" value={item.policyId} valueClass="text-purple-400" />
          <Row label="Policy Name" value={item.policyName} valueClass="text-slate-300" />
          <Row label="Spend Ceiling" value={item.spendLimit} valueClass="text-emerald-400 font-bold" />
        </InspectorSection>

        {/* SECTION 03: PROCESSOR & ROUTING */}
        <InspectorSection title="03 — PROCESSOR & ROUTING" icon={Activity} color="text-emerald-400">
          <Row label="Primary Processor" value={item.processor} valueClass="text-slate-200 font-bold" />
          <Row label="Processor Ref" value={item.processorReference} valueClass="text-slate-400" />
          <Row label="Currency / Country" value={`${item.currency} / ${item.country}`} valueClass="text-slate-300" />
          <Row label="3DS Status" value={item.threeDsStatus} valueClass="text-blue-300" />
          <Row label="AVS / CVV Check" value={item.avsCvvResult} valueClass="text-emerald-400 font-bold" />
        </InspectorSection>

        {/* SECTION 04: SECURITY & TOKENIZATION */}
        <InspectorSection title="04 — ZERO-TRUST PCI SECURITY" icon={ShieldCheck} color="text-emerald-400">
          <Row label="Tokenization Status" value={item.tokenStatus} valueClass="text-emerald-400 font-bold" />
          <Row label="Token Reference" value={item.tokenId} valueClass="text-blue-400" />
          <Row label="Vault Reference" value={`vault_${item.instrumentId.toLowerCase()}`} valueClass="text-purple-400" />
          <Row label="PCI Scope" value="OUT_OF_SCOPE (EMVCo Tokenized)" valueClass="text-emerald-400" />
        </InspectorSection>

        {/* SECTION 05: FRAUDGUARD RISK */}
        <InspectorSection title="05 — FRAUDGUARD RISK EVALUATION" icon={AlertTriangle} color={item.riskScore < 30 ? 'text-emerald-400' : item.riskScore < 70 ? 'text-amber-400' : 'text-red-400'}>
          <div className="flex items-center gap-3 mb-2">
            <div className={`text-3xl font-bold font-display ${item.riskScore < 30 ? 'text-emerald-400' : item.riskScore < 70 ? 'text-amber-400' : 'text-red-400'}`}>
              {item.riskScore} / 100
            </div>
            <div>
              <div className="text-[9px] text-slate-500 uppercase">RISK TIER</div>
              <div className={`text-xs font-bold ${item.riskTier === 'LOW' ? 'text-emerald-400' : item.riskTier === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'}`}>
                {item.riskTier} RISK
              </div>
            </div>
          </div>
          <Row label="Velocity Flag" value="CLEAR" valueClass="text-emerald-400" />
          <Row label="Geo Mismatch" value="CLEAR" valueClass="text-emerald-400" />
          <Row label="Agent Behavior" value="NORMAL" valueClass="text-emerald-400" />
        </InspectorSection>

      </div>
    </AGDrawer>
  );
}

function InspectorSection({ title, icon: Icon, color, children }: { title: string; icon: any; color: string; children: React.ReactNode; }) {
  return (
    <div className="p-4 rounded-xl bg-slate-950/80 border border-white/[0.06] space-y-2">
      <h4 className={`font-bold text-[11px] uppercase tracking-wider flex items-center gap-1.5 font-mono ${color}`}>
        <Icon className="w-3.5 h-3.5" /> {title}
      </h4>
      {children}
    </div>
  );
}

function Row({ label, value, valueClass = 'text-slate-300' }: { label: string; value: string; valueClass?: string; }) {
  return (
    <div className="flex justify-between items-center py-0.5">
      <span className="text-[10px] text-slate-500">{label}:</span>
      <span className={`text-[10px] font-mono ${valueClass} max-w-[60%] text-right truncate`}>{value}</span>
    </div>
  );
}
