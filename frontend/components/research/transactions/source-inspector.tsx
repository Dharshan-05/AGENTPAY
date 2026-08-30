'use client';

import { useEffect } from 'react';
import { SourceTransactionRecord, SourceTransactionDetail } from './source-types';
import {
  X, Shield, CreditCard, Zap, User, Building2, CheckCircle2, XCircle,
  Clock, AlertTriangle, BookOpen, Lock, ArrowRight, Activity
} from 'lucide-react';

interface SourceInspectorProps {
  transaction: SourceTransactionRecord | null;
  detail?: SourceTransactionDetail | null;
  onClose: () => void;
}

function Field({ label, value, mono = false, highlight }: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
  highlight?: 'emerald' | 'blue' | 'rose' | 'amber';
}) {
  const colorMap: Record<string, string> = {
    emerald: 'text-emerald-700 font-bold',
    blue: 'text-blue-700 font-bold',
    rose: 'text-rose-700 font-bold',
    amber: 'text-amber-700 font-bold',
  };
  return (
    <div className="flex items-start justify-between gap-2 py-1.5 border-b border-slate-100 last:border-0">
      <span className="text-[10px] text-slate-400 uppercase tracking-wide font-bold flex-shrink-0">{label}</span>
      <span className={`text-[11px] text-right ${mono ? 'font-mono' : 'font-sans'} ${highlight ? colorMap[highlight] : 'text-slate-800 font-semibold'}`}>
        {value}
      </span>
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="space-y-0.5">
      <div className="flex items-center gap-1.5 mb-2">
        <div className="text-slate-400">{icon}</div>
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{title}</span>
      </div>
      <div className="bg-slate-50 rounded-xl border border-slate-100 px-3 py-2 space-y-0">
        {children}
      </div>
    </div>
  );
}

function riskColor(score: number) {
  if (score < 30) return 'text-emerald-700';
  if (score < 60) return 'text-amber-700';
  if (score < 80) return 'text-orange-700';
  return 'text-rose-700';
}

export function SourceInspector({ transaction, detail, onClose }: SourceInspectorProps) {
  // ESC key support
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  if (!transaction) return null;

  const d = detail;

  return (
    <div
      className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex justify-end font-sans"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      role="dialog"
      aria-modal="true"
      aria-label="Transaction Inspector"
    >
      <div className="w-full max-w-lg bg-white h-full shadow-2xl flex flex-col overflow-hidden">
        {/* HEADER */}
        <div className="flex items-start justify-between px-5 py-4 border-b border-slate-200 flex-shrink-0">
          <div>
            <div className="text-[9px] uppercase tracking-widest text-slate-400 font-bold mb-1">TRANSACTION INSPECTOR</div>
            <h2 className="text-base font-bold text-slate-900 font-mono">{transaction.transactionId}</h2>
            <div className="flex items-center gap-2 mt-1 flex-wrap">
              <span className="font-mono text-xs font-bold text-blue-600">{transaction.paymentIntentId}</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                transaction.status === 'SETTLED' || transaction.status === 'CAPTURED' || transaction.status === 'AUTHORIZED'
                  ? 'bg-emerald-100 text-emerald-800'
                  : transaction.status === 'BLOCKED' || transaction.status === 'FAILED'
                  ? 'bg-rose-100 text-rose-800'
                  : transaction.status === 'UNDER_REVIEW' || transaction.status === 'REQUIRES_ACTION'
                  ? 'bg-amber-100 text-amber-800'
                  : 'bg-slate-100 text-slate-700'
              }`}>
                {transaction.status}
              </span>
              <span className="text-[9px] text-slate-400 font-mono">{transaction.environment}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors"
            aria-label="Close inspector"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* AMOUNT OVERVIEW */}
        <div className="grid grid-cols-3 gap-0 border-b border-slate-200 flex-shrink-0">
          <div className="p-3.5 text-center border-r border-slate-100">
            <div className="text-[9px] text-slate-400 uppercase font-bold">REQUESTED</div>
            <div className="text-sm font-bold text-slate-900 font-mono mt-1">{transaction.requestedAmount}</div>
          </div>
          <div className="p-3.5 text-center border-r border-slate-100">
            <div className="text-[9px] text-slate-400 uppercase font-bold">AUTHORIZED</div>
            <div className="text-sm font-bold text-emerald-700 font-mono mt-1">{transaction.authorizedAmount}</div>
          </div>
          <div className="p-3.5 text-center">
            <div className="text-[9px] text-slate-400 uppercase font-bold">CAPTURED</div>
            <div className="text-sm font-bold text-blue-700 font-mono mt-1">{transaction.capturedAmount}</div>
          </div>
        </div>

        {/* SCROLLABLE BODY */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
          
          {/* AGENT */}
          <Section title="Agent" icon={<User className="w-3.5 h-3.5" />}>
            <Field label="Agent ID" value={transaction.agentId} mono highlight="blue" />
            <Field label="Agent Name" value={transaction.agentName} />
            <Field label="Policy Binding" value={transaction.policyBinding} mono />
            <Field label="Environment" value={transaction.environment} mono />
          </Section>

          {/* PARTICIPANTS */}
          <Section title="Participants" icon={<Building2 className="w-3.5 h-3.5" />}>
            <Field label="Merchant" value={transaction.merchant} />
            <Field label="Customer" value={transaction.customer} />
            <Field label="Region" value={transaction.region} mono />
          </Section>

          {/* PAYMENT METHOD */}
          <Section title="Payment Method" icon={<CreditCard className="w-3.5 h-3.5" />}>
            <Field label="Method" value={transaction.paymentMethod.replace(/_/g, ' ')} mono />
            <Field label="Detail" value={transaction.paymentMethodDetail} mono />
            <Field label="Currency" value={transaction.currency} mono />
            <Field label="Processor" value={transaction.processor} />
            <Field label="Processor Ref" value={transaction.processorReference} mono />
            <Field label="Attempt Count" value={`${transaction.attemptCount}`} mono />
            <Field label="Response Code" value={transaction.responseCode} mono
              highlight={transaction.responseCode === '00' ? 'emerald' : 'rose'} />
          </Section>

          {/* AUTHORIZATION */}
          {d?.authorization && (
            <Section title="Authorization" icon={<CheckCircle2 className="w-3.5 h-3.5" />}>
              <Field label="Auth ID" value={d.authorization.authorizationId} mono />
              <Field label="Auth Code" value={d.authorization.authorizationCode} mono highlight="emerald" />
              <Field label="Requested" value={d.authorization.requestedAmount} mono />
              <Field label="Authorized" value={d.authorization.authorizedAmount} mono highlight="emerald" />
              <Field label="3DS Status" value={d.authorization.threeDsStatus} mono
                highlight={d.authorization.threeDsStatus === 'AUTHENTICATED' ? 'emerald' : 'rose'} />
              <Field label="AVS Result" value={d.authorization.avsResult} mono
                highlight={d.authorization.avsResult === 'MATCH' ? 'emerald' : 'amber'} />
              <Field label="CVV Result" value={d.authorization.cvvResult} mono
                highlight={d.authorization.cvvResult === 'MATCH' ? 'emerald' : 'amber'} />
              <Field label="Human Approval" value={d.authorization.humanApproval || 'NOT_REQUIRED'} mono />
              <Field label="Timestamp" value={d.authorization.timestamp} mono />
            </Section>
          )}

          {/* CAPTURE */}
          {d?.capture && (
            <Section title="Capture" icon={<Zap className="w-3.5 h-3.5" />}>
              <Field label="Capture ID" value={d.capture.captureId} mono />
              <Field label="Type" value={d.capture.captureType} mono />
              <Field label="Captured" value={d.capture.capturedAmount} mono highlight="blue" />
              <Field label="Original" value={d.capture.originalAmount} mono />
              <Field label="Status" value={d.capture.status} mono
                highlight={d.capture.status === 'CAPTURED' ? 'emerald' : 'rose'} />
              {d.capture.settlementReference && (
                <Field label="Settlement Ref" value={d.capture.settlementReference} mono highlight="blue" />
              )}
              <Field label="Timestamp" value={d.capture.timestamp} mono />
            </Section>
          )}

          {/* RISK */}
          <Section title="Risk Assessment" icon={<Shield className="w-3.5 h-3.5" />}>
            <Field label="Risk Score" value={
              <span className={`font-bold font-mono ${riskColor(transaction.riskScore)}`}>
                {transaction.riskScore} / 100
              </span>
            } />
            <Field label="Risk Tier" value={transaction.riskTier} mono
              highlight={transaction.riskTier === 'LOW' ? 'emerald' : transaction.riskTier === 'HIGH' || transaction.riskTier === 'CRITICAL' ? 'rose' : 'amber'} />
            {d?.risk && (
              <>
                <Field label="Velocity Flag" value={d.risk.velocityFlag ? '⚠️ YES' : '✓ NO'}
                  highlight={d.risk.velocityFlag ? 'rose' : 'emerald'} />
                <Field label="Geo Risk" value={d.risk.geoRiskFlag ? '⚠️ YES' : '✓ NO'}
                  highlight={d.risk.geoRiskFlag ? 'rose' : 'emerald'} />
                <Field label="Device Risk" value={d.risk.deviceRiskFlag ? '⚠️ YES' : '✓ NO'}
                  highlight={d.risk.deviceRiskFlag ? 'rose' : 'emerald'} />
                <Field label="Agent Risk" value={d.risk.agentRiskFlag ? '⚠️ YES' : '✓ NO'}
                  highlight={d.risk.agentRiskFlag ? 'rose' : 'emerald'} />
                <Field label="Fraud Signals" value={d.risk.fraudSignals.length > 0 ? d.risk.fraudSignals.join(', ') : 'NONE'}
                  highlight={d.risk.fraudSignals.length > 0 ? 'rose' : 'emerald'} />
                <Field label="Evaluated By" value={d.risk.evaluatedBy} />
              </>
            )}
          </Section>

          {/* POLICY */}
          <Section title="Policy Decision" icon={<Lock className="w-3.5 h-3.5" />}>
            <Field label="Policy ID" value={transaction.policyBinding} mono />
            {d?.policy && (
              <>
                <Field label="Policy Name" value={d.policy.policyName} />
                <Field label="Decision" value={d.policy.decision} mono
                  highlight={d.policy.decision === 'APPROVED' ? 'emerald' : d.policy.decision === 'BLOCKED' ? 'rose' : 'amber'} />
                <Field label="Spend Limit" value={d.policy.spendLimit} mono />
                <Field label="Applied Rule" value={d.policy.appliedRule} mono />
                <Field label="HITL Required" value={d.policy.approvalRequired ? 'YES' : 'NO'}
                  highlight={d.policy.approvalRequired ? 'amber' : 'emerald'} />
                <Field label="Decision Reason" value={d.policy.decisionReason} />
                <Field label="Evaluated At" value={d.policy.evaluatedAt} mono />
              </>
            )}
          </Section>

          {/* SETTLEMENT */}
          {transaction.settlementId && (
            <Section title="Settlement" icon={<Activity className="w-3.5 h-3.5" />}>
              <Field label="Settlement ID" value={transaction.settlementId} mono highlight="blue" />
              <Field label="Status" value="SETTLED" mono highlight="emerald" />
              <Field label="References" value="/reconciliation" mono />
            </Section>
          )}

          {/* METADATA */}
          {d?.metadata && d.metadata.length > 0 && (
            <Section title="Transaction Metadata" icon={<BookOpen className="w-3.5 h-3.5" />}>
              {d.metadata.map((m) => (
                <Field key={m.key} label={m.key} value={m.value} mono />
              ))}
            </Section>
          )}

          {/* CROSS-MODULE LINKS */}
          <div className="bg-slate-50 rounded-xl border border-slate-200 p-3 space-y-2">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Cross-Module References</div>
            <div className="grid grid-cols-2 gap-1.5 text-[10px]">
              <a className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold">
                <ArrowRight className="w-3 h-3" /> /agents · {transaction.agentId}
              </a>
              <a className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold">
                <ArrowRight className="w-3 h-3" /> /agentguard · {transaction.policyBinding}
              </a>
              <a className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold">
                <ArrowRight className="w-3 h-3" /> /fraudguard · Risk {transaction.riskScore}
              </a>
              {transaction.settlementId && (
                <a className="flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold">
                  <ArrowRight className="w-3 h-3" /> /reconciliation · {transaction.settlementId}
                </a>
              )}
            </div>
          </div>

          {/* TIMESTAMPS */}
          <Section title="Timestamps" icon={<Clock className="w-3.5 h-3.5" />}>
            <Field label="Created" value={transaction.createdTimestamp} mono />
            <Field label="Updated" value={transaction.updatedTimestamp} mono />
          </Section>
        </div>

        {/* FOOTER */}
        <div className="border-t border-slate-200 px-5 py-3 flex items-center justify-between flex-shrink-0 bg-slate-50">
          <span className="text-[10px] text-slate-400 font-mono">ESC or click outside to close</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 text-white font-bold rounded-xl text-xs hover:bg-slate-700 transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
