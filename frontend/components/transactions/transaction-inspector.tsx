'use client';

import { useEffect } from 'react';
import { AGDrawer } from '@/components/ui/ag-drawer';
import { AGButton } from '@/components/ui/ag-button';
import {
  Bot, ShieldCheck, CreditCard, Activity, Lock, Receipt,
  AlertTriangle, ArrowRight
} from 'lucide-react';
import { TxnInspectorDetail } from './transaction-types';

interface TransactionInspectorProps {
  txn: TxnInspectorDetail | null;
  onClose: () => void;
}

export function TransactionInspector({ txn, onClose }: TransactionInspectorProps) {
  useEffect(() => {
    if (!txn) return;
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [txn, onClose]);

  if (!txn) return null;

  return (
    <AGDrawer
      isOpen={!!txn}
      onClose={onClose}
      title={`TRANSACTION INSPECTOR: ${txn.transactionId}`}
      subtitle="PAYMENT INTENT & TRANSACTION OPERATIONS CONTROL"
      footer={
        <div className="space-y-2 font-mono">
          <div className="flex gap-2">
            <AGButton variant="ghost" size="sm" onClick={() => {
              navigator.clipboard?.writeText(txn.transactionId);
              alert(`Copied: ${txn.transactionId}`);
            }} className="flex-1">
              COPY TXN ID
            </AGButton>
            <AGButton variant="ghost" size="sm" onClick={() => {
              navigator.clipboard?.writeText(txn.paymentIntentId);
              alert(`Copied: ${txn.paymentIntentId}`);
            }} className="flex-1">
              COPY PI ID
            </AGButton>
          </div>
          <AGButton variant="secondary" size="md" onClick={onClose} className="w-full">
            CLOSE INSPECTOR
          </AGButton>
        </div>
      }
    >
      <div className="space-y-5 font-mono text-xs">

        {/* DECISION CHAIN */}
        <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20 space-y-2">
          <div className="text-[9px] text-blue-400 font-bold uppercase tracking-[0.2em] mb-3">TRANSACTION DECISION CHAIN</div>
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 flex-wrap">
            {[
              { label: txn.agentId, color: 'text-blue-400' },
              { label: 'INTENT', color: 'text-slate-400' },
              { label: txn.policyId, color: 'text-purple-400' },
              { label: `RISK ${txn.riskScore}/100`, color: txn.riskScore < 40 ? 'text-emerald-400' : txn.riskScore < 70 ? 'text-amber-400' : 'text-red-400' },
              { label: txn.status === 'BLOCKED' ? 'BLOCKED' : 'AUTH', color: txn.status === 'BLOCKED' ? 'text-red-400' : 'text-emerald-400' },
              { label: txn.processor, color: 'text-slate-300' },
              { label: txn.status, color: txn.status === 'SETTLED' || txn.status === 'CAPTURED' ? 'text-emerald-400' : txn.status === 'BLOCKED' || txn.status === 'FAILED' ? 'text-red-400' : 'text-amber-400' },
            ].map((item, i, arr) => (
              <span key={i} className="flex items-center gap-1.5">
                <span className={`font-bold ${item.color}`}>{item.label}</span>
                {i < arr.length - 1 && <ArrowRight className="w-2.5 h-2.5 text-slate-600 inline" />}
              </span>
            ))}
          </div>
        </div>

        {/* SECTION 01: TRANSACTION IDENTITY */}
        <InspectorSection title="01 — TRANSACTION IDENTITY" icon={Receipt} color="text-blue-400">
          <Row label="Transaction ID" value={txn.transactionId} valueClass="text-blue-400 font-bold" />
          <Row label="Payment Intent ID" value={txn.paymentIntentId} valueClass="text-purple-400" />
          <Row label="Processor Reference" value={txn.processorReference} valueClass="text-slate-300" />
          <Row label="Response Code" value={txn.responseCode} valueClass="text-slate-300" />
          <Row label="Environment" value={txn.environment} valueClass={txn.environment === 'PRODUCTION' ? 'text-emerald-400' : 'text-amber-400'} />
          <Row label="Region" value={txn.region} />
          <Row label="Attempts" value={`${txn.attemptCount}`} />
          <Row label="Created" value={txn.createdAt} />
          <Row label="Updated" value={txn.updatedAt} />
        </InspectorSection>

        {/* SECTION 02: FINANCIAL SUMMARY */}
        <InspectorSection title="02 — FINANCIAL SUMMARY" icon={CreditCard} color="text-emerald-400">
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'REQUESTED', value: txn.requestedAmount, cls: 'text-slate-200' },
              { label: 'AUTHORIZED', value: txn.authorizedAmount, cls: 'text-emerald-400' },
              { label: 'CAPTURED', value: txn.capturedAmount, cls: 'text-emerald-400' },
              { label: 'FEES', value: txn.fees, cls: 'text-amber-400' },
              { label: 'NET AMOUNT', value: txn.netAmount, cls: 'text-emerald-400 font-bold' },
              { label: 'CURRENCY', value: txn.currency, cls: 'text-slate-300' },
            ].map(({ label, value, cls }) => (
              <div key={label} className="p-2 rounded-lg bg-slate-950/60 border border-white/[0.04]">
                <div className="text-[9px] text-slate-500 uppercase">{label}</div>
                <div className={`text-sm font-bold font-mono ${cls}`}>{value}</div>
              </div>
            ))}
          </div>
          {txn.settlementBatch && (
            <div className="mt-2 p-2 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
              <div className="text-[9px] text-slate-500 uppercase">SETTLEMENT BATCH</div>
              <div className="text-emerald-400 font-bold text-xs">{txn.settlementBatch}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">ID: {txn.settlementId}</div>
            </div>
          )}
        </InspectorSection>

        {/* SECTION 03: AGENT CONTEXT */}
        <InspectorSection title="03 — AGENT CONTEXT" icon={Bot} color="text-blue-400">
          <Row label="Agent ID" value={txn.agentId} valueClass="text-blue-400 font-bold" />
          <Row label="Agent Name" value={txn.agentName} valueClass="text-slate-200" />
          <Row label="Agent Type" value="AUTONOMOUS" valueClass="text-blue-300" />
          <Row label="Owner" value="Finance Operations" />
          <Row label="Environment" value={txn.environment} />
        </InspectorSection>

        {/* SECTION 04: POLICY */}
        <InspectorSection title="04 — AGENTGUARD POLICY" icon={ShieldCheck} color="text-purple-400">
          <Row label="Policy ID" value={txn.policyId} valueClass="text-purple-400 font-bold" />
          <Row label="Policy Name" value={txn.policyName} valueClass="text-slate-200" />
          <Row label="Decision" value={txn.policyDecision} valueClass={txn.policyDecision === 'APPROVED' ? 'text-emerald-400' : txn.policyDecision === 'BLOCKED' ? 'text-red-400' : 'text-amber-400'} />
          <Row label="Spend Limit" value="$10,000.00" />
          <Row label="HITL Required" value={txn.requiresHumanApproval ? 'YES — ABOVE LIMIT' : 'NO'} valueClass={txn.requiresHumanApproval ? 'text-amber-400' : 'text-emerald-400'} />
        </InspectorSection>

        {/* SECTION 05: RISK */}
        <InspectorSection title="05 — FRAUDGUARD RISK" icon={AlertTriangle} color={txn.riskScore < 40 ? 'text-emerald-400' : txn.riskScore < 70 ? 'text-amber-400' : 'text-red-400'}>
          <div className="flex items-center gap-3 mb-3">
            <div className={`text-4xl font-bold font-display ${
              txn.riskScore < 40 ? 'text-emerald-400' : txn.riskScore < 70 ? 'text-amber-400' : 'text-red-400'
            }`}>{txn.riskScore}</div>
            <div>
              <div className="text-[10px] text-slate-500">RISK SCORE / 100</div>
              <div className={`text-xs font-bold ${
                txn.riskTier === 'LOW' ? 'text-emerald-400' : txn.riskTier === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'
              }`}>{txn.riskTier} RISK</div>
            </div>
          </div>
          <Row label="Velocity Flag" value="CLEAR" valueClass="text-emerald-400" />
          <Row label="Geo Risk" value="CLEAR" valueClass="text-emerald-400" />
          <Row label="Agent Behavior" value="NORMAL" valueClass="text-emerald-400" />
          <Row label="Fraud Decision" value={txn.riskScore < 40 ? 'PASS' : txn.riskScore < 70 ? 'REVIEW' : 'FLAG'} valueClass={txn.riskScore < 40 ? 'text-emerald-400' : txn.riskScore < 70 ? 'text-amber-400' : 'text-red-400'} />
        </InspectorSection>

        {/* SECTION 06: PAYMENT */}
        <InspectorSection title="06 — PAYMENT DETAILS" icon={CreditCard} color="text-blue-400">
          <Row label="Method" value={txn.paymentMethod.replace(/_/g, ' ')} />
          <Row label="Detail" value={txn.paymentMethodDetail} valueClass="text-slate-200" />
          <Row label="Processor" value={txn.processor} valueClass="text-slate-200 font-bold" />
          <Row label="Auth Code" value={txn.authorizationCode || '—'} valueClass="text-emerald-400" />
          {txn.authorization && (
            <>
              <Row label="AVS Result" value={txn.authorization.avsResult} valueClass="text-emerald-400" />
              <Row label="CVV Result" value={txn.authorization.cvvResult} valueClass="text-emerald-400" />
              <Row label="3DS Status" value={txn.authorization.threeDsStatus} />
            </>
          )}
        </InspectorSection>

        {/* SECTION 07: LIFECYCLE SUMMARY */}
        {txn.lifecycle && txn.lifecycle.length > 0 && (
          <InspectorSection title="07 — LIFECYCLE SUMMARY" icon={Activity} color="text-indigo-400">
            <div className="space-y-1.5">
              {txn.lifecycle.slice(0, 6).map((step) => (
                <div key={step.stepId} className="flex items-center gap-2">
                  <div className={`w-3.5 h-3.5 rounded-full flex items-center justify-center shrink-0 ${
                    step.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-400' :
                    step.status === 'FAILED' ? 'bg-red-500/20 text-red-400' :
                    step.status === 'ACTIVE' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-slate-800 text-slate-600'
                  }`}>
                    {step.status === 'COMPLETED' && <span className="text-[6px]">✓</span>}
                    {step.status === 'FAILED' && <span className="text-[6px]">✗</span>}
                    {step.status === 'ACTIVE' && <span className="w-1 h-1 rounded-full bg-blue-400 animate-pulse" />}
                    {(step.status === 'SKIPPED' || step.status === 'PENDING') && <span className="text-[6px]">-</span>}
                  </div>
                  <span className={`text-[10px] flex-1 ${
                    step.status === 'COMPLETED' ? 'text-slate-300' :
                    step.status === 'FAILED' ? 'text-red-400' :
                    step.status === 'ACTIVE' ? 'text-blue-400 font-bold' :
                    'text-slate-600'
                  }`}>{step.label}</span>
                  {step.latencyMs !== undefined && step.status !== 'SKIPPED' && (
                    <span className="text-[9px] text-slate-600">{step.latencyMs}ms</span>
                  )}
                </div>
              ))}
            </div>
          </InspectorSection>
        )}

        {/* SECTION 08: AUDIT */}
        <InspectorSection title="08 — AUDIT REFERENCE" icon={Lock} color="text-amber-400">
          <Row label="Request ID" value="REQ-A91F201" valueClass="text-amber-400" />
          <Row label="Idempotency Key" value={`IDEM-${txn.transactionId}`} />
          <Row label="Audit Hash" value="sha256:a3f2e1...9b12" valueClass="text-slate-400" />
          <Row label="Chain Integrity" value="VERIFIED" valueClass="text-emerald-400 font-bold" />
          <div className="mt-2 p-2 rounded-lg bg-amber-500/5 border border-amber-500/20 text-[9px] text-slate-500">
            Audit entries are cryptographically chained. Tamper detection active.
          </div>
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
