"use client";

import { useState } from "react";
import {
  Shield,
  Scale,
  CheckCircle2,
  FileText,
  AlertTriangle,
  Lock,
  Radio,
  ChevronDown,
  ChevronUp,
  Cpu,
  Activity,
  Zap,
} from "lucide-react";
import "./sentinelx.css";

interface PolicyPack {
  id: string;
  name: string;
  regulation: string;
  category: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  description: string;
  enabled: boolean;
  violationsCount: number;
  protectedFields: string[];
  rules: { id: string; description: string; severity: string }[];
}

const POLICIES: PolicyPack[] = [
  {
    id: "pol_gdpr",
    name: "GDPR Compliance & PII Protection",
    regulation: "GDPR",
    category: "Data Privacy",
    severity: "CRITICAL",
    description: "Detects and redacts Personally Identifiable Information (PII) including names, emails, phone numbers, and location telemetry before LLM ingestion.",
    enabled: true,
    violationsCount: 142,
    protectedFields: ["Names & emails", "Phone numbers", "Location data", "Device identifiers"],
    rules: [
      { id: "RULE_GDPR_01", description: "Block raw email addresses in prompt payload", severity: "CRITICAL" },
      { id: "RULE_GDPR_02", description: "Redact EU passport and national ID patterns", severity: "HIGH" },
    ],
  },
  {
    id: "pol_pci",
    name: "PCI DSS v4.0 Payment Guard",
    regulation: "PCI DSS",
    category: "Payment Security",
    severity: "CRITICAL",
    description: "Enforces strict cardholder data firewalling. Prevents raw credit card numbers (PAN), CVV codes, and expiry dates from leaking into model context.",
    enabled: true,
    violationsCount: 89,
    protectedFields: ["Card numbers (PAN)", "CVV", "Expiry dates", "Cardholder name"],
    rules: [
      { id: "RULE_PCI_01", description: "Block 16-digit Luhn-valid primary account numbers", severity: "CRITICAL" },
      { id: "RULE_PCI_02", description: "Scrub 3/4-digit card verification values", severity: "CRITICAL" },
    ],
  },
  {
    id: "pol_hipaa",
    name: "HIPAA Protected Health Information",
    regulation: "HIPAA",
    category: "Healthcare Privacy",
    severity: "HIGH",
    description: "Monitors medical records, diagnostic codes, patient identifiers, and prescription data against unauthorized AI disclosure.",
    enabled: true,
    violationsCount: 24,
    protectedFields: ["Patient identifiers", "Diagnoses", "Prescriptions", "Insurance data"],
    rules: [
      { id: "RULE_HIPAA_01", description: "Redact ICD-10 medical diagnostic codes", severity: "HIGH" },
    ],
  },
  {
    id: "pol_soc2",
    name: "SOC 2 Type II Credentials Firewall",
    regulation: "SOC 2",
    category: "Security Controls",
    severity: "HIGH",
    description: "Scans for hardcoded credentials, JWT access tokens, database connection strings, and config secrets in prompts.",
    enabled: true,
    violationsCount: 67,
    protectedFields: ["Credentials", "Customer data", "Access tokens", "Config secrets"],
    rules: [
      { id: "RULE_SOC2_01", description: "Block AWS/GCP API access key signatures", severity: "CRITICAL" },
    ],
  },
  {
    id: "pol_iso",
    name: "ISO 27001 Secret Pattern Library",
    regulation: "ISO 27001",
    category: "Information Security",
    severity: "MEDIUM",
    description: "Detects private RSA keys, SSH keypairs, and internal API bearer tokens across all agent execution channels.",
    enabled: false,
    violationsCount: 12,
    protectedFields: ["API keys", "Private keys", "Passwords", "Connection strings"],
    rules: [
      { id: "RULE_ISO_01", description: "Scrub PEM private key headers", severity: "HIGH" },
    ],
  },
];

const DETECTION_RULES = [
  { id: "SIG_001", name: "Adversarial Prompt Injection Vector", category: "Jailbreak", hits: 342, severity: "CRITICAL" },
  { id: "SIG_002", name: "System Prompt Extraction Override", category: "Exfiltration", hits: 189, severity: "HIGH" },
  { id: "SIG_003", name: "Credit Card PAN (Luhn Algorithm)", category: "PCI DSS", hits: 89, severity: "CRITICAL" },
  { id: "SIG_004", name: "AWS Secret Access Key Pattern", category: "Secrets", hits: 56, severity: "CRITICAL" },
  { id: "SIG_005", name: "SSN / Tax Identification Number", category: "PII", hits: 45, severity: "HIGH" },
  { id: "SIG_006", name: "JWT Bearer Token Signature", category: "Secrets", hits: 112, severity: "MEDIUM" },
];

export default function SentinelXResearchPage() {
  const [policies, setPolicies] = useState<PolicyPack[]>(POLICIES);
  const [expandedId, setExpandedId] = useState<string | null>("pol_gdpr");
  const [activeTab, setActiveTab] = useState("policies");

  const togglePolicy = (id: string) => {
    setPolicies((prev) =>
      prev.map((p) => (p.id === id ? { ...p, enabled: !p.enabled } : p))
    );
  };

  return (
    <div className="sentinelx-root font-sans text-slate-100">
      
      {/* SentinelX Top Header Navigation Bar */}
      <header className="h-16 border-b border-white/[0.08] bg-slate-950/80 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold font-mono">
            SX
          </div>
          <div>
            <h1 className="font-bold text-sm text-slate-100 tracking-wider flex items-center gap-2">
              SENTINEL<span className="text-blue-400">X</span>
              <span className="text-[10px] font-mono text-slate-400 font-normal">
                AI Governance Firewall & Policy Control
              </span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-mono font-bold">
            <Radio className="w-3 h-3 animate-pulse" /> FIREWALL ENFORCING
          </div>
          <span className="text-xs font-mono text-slate-400">v2.4.0-Production</span>
        </div>
      </header>

      {/* Main Container Layout */}
      <div className="max-w-7xl mx-auto p-6 md:p-8 space-y-8">
        
        {/* Page Title & Description */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/[0.08]">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2">
              <Scale className="w-6 h-6 text-blue-400" /> POLICY CENTER & FIREWALL PACKS
            </h2>
            <p className="text-xs font-mono text-slate-400 mt-1">
              Regulatory and corporate policy packs enforced on every prompt payload before model ingestion.
            </p>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="px-3 py-1.5 rounded-lg bg-slate-900 border border-white/10 text-slate-300">
              Active Packs: <strong className="text-emerald-400">{policies.filter((p) => p.enabled).length} / {policies.length}</strong>
            </span>
          </div>
        </div>

        {/* Policy Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column (8 cols): Enforced Policy Packs */}
          <div className="lg:col-span-8 space-y-4">
            <div className="flex items-center justify-between pb-2 font-mono text-xs">
              <span className="text-slate-300 font-bold uppercase tracking-wider">
                ENFORCED POLICY PACKS
              </span>
              <span className="text-slate-500 text-[10px]">
                Enforced in order of severity · Live toggles active
              </span>
            </div>

            <div className="space-y-3">
              {policies.map((p) => {
                const isExpanded = expandedId === p.id;
                return (
                  <div
                    key={p.id}
                    className={`rounded-xl border transition-all overflow-hidden ${
                      p.enabled
                        ? "bg-slate-900/60 border-white/[0.08]"
                        : "bg-slate-950/40 border-white/[0.04] opacity-60"
                    }`}
                  >
                    {/* Policy Summary Row */}
                    <div className="p-4 flex items-center justify-between gap-4">
                      <button
                        onClick={() => setExpandedId(isExpanded ? null : p.id)}
                        className="flex items-center gap-3 text-left flex-1 min-w-0"
                      >
                        <div
                          className={`w-9 h-9 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                            p.severity === "CRITICAL"
                              ? "bg-red-500/10 text-red-400 border border-red-500/30"
                              : p.severity === "HIGH"
                              ? "bg-orange-500/10 text-orange-400 border border-orange-500/30"
                              : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                          }`}
                        >
                          <Scale className="w-4 h-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-slate-100">{p.name}</span>
                            <span className="px-2 py-0.5 rounded text-[9px] font-mono bg-white/[0.04] border border-white/10 text-slate-300">
                              {p.regulation}
                            </span>
                          </div>
                          <p className="text-xs font-mono text-slate-400 truncate mt-0.5">{p.description}</p>
                        </div>
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-slate-500" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-slate-500" />
                        )}
                      </button>

                      {/* Enable/Disable Toggle Switch */}
                      <div className="flex items-center gap-4 border-l border-white/[0.08] pl-4">
                        <div className="text-right font-mono text-[10px]">
                          <span className="text-red-400 block font-bold">{p.violationsCount} violations</span>
                          <span className="text-slate-500">Weight: {p.severity}</span>
                        </div>
                        <button
                          onClick={() => togglePolicy(p.id)}
                          className={`w-11 h-6 rounded-full transition-colors relative p-0.5 ${
                            p.enabled ? "bg-emerald-500" : "bg-slate-800"
                          }`}
                        >
                          <div
                            className={`w-5 h-5 rounded-full bg-slate-950 transition-transform ${
                              p.enabled ? "translate-x-5" : "translate-x-0"
                            }`}
                          />
                        </button>
                      </div>
                    </div>

                    {/* Expanded Policy Details Drawer */}
                    {isExpanded && (
                      <div className="p-4 border-t border-white/[0.06] bg-slate-950/80 space-y-4 font-mono text-xs">
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1.5 font-bold">
                            PROTECTED SENSITIVE FIELDS
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {p.protectedFields.map((f) => (
                              <span
                                key={f}
                                className="px-2 py-1 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px]"
                              >
                                {f}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div>
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider block mb-1.5 font-bold">
                            ENFORCEMENT SIGNATURE RULES
                          </span>
                          <div className="space-y-1.5">
                            {p.rules.map((r) => (
                              <div
                                key={r.id}
                                className="p-2 rounded-lg bg-slate-900/60 border border-white/[0.04] flex items-center justify-between"
                              >
                                <div className="flex items-center gap-2">
                                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                                  <span className="text-slate-200">{r.description}</span>
                                </div>
                                <span className="text-[9px] text-slate-500">{r.id}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column (4 cols): Detection Rules & Enforcement Pipeline */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Signature Library */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-white/[0.08] space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/[0.08]">
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-200 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-blue-400" /> DETECTION RULES LIBRARY
                </h3>
                <span className="text-[10px] font-mono text-slate-400">30+ Patterns</span>
              </div>

              <div className="space-y-2 max-h-[300px] overflow-y-auto font-mono text-xs">
                {DETECTION_RULES.map((r) => (
                  <div
                    key={r.id}
                    className="p-2.5 rounded-lg bg-slate-950/60 border border-white/[0.04] flex items-center justify-between"
                  >
                    <div>
                      <span className="font-bold text-slate-200 block text-[11px]">{r.name}</span>
                      <span className="text-[9px] text-slate-500">{r.category}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] text-emerald-400 font-bold block">{r.hits} hits</span>
                      <span className="text-[9px] text-slate-500">{r.severity}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Real-Time Enforcement Flow Step Diagram */}
            <div className="p-5 rounded-xl bg-slate-900/60 border border-white/[0.08] space-y-4">
              <h3 className="font-bold text-xs uppercase tracking-wider text-slate-200 flex items-center gap-2 pb-3 border-b border-white/[0.08]">
                <Activity className="w-4 h-4 text-emerald-400" /> ENFORCEMENT PIPELINE FLOW
              </h3>

              <div className="space-y-2.5 font-mono text-xs">
                {[
                  "1. Prompt Payload Ingestion",
                  "2. Secret & PII Scanning (30+ Rules)",
                  "3. Regulatory Policy Pack Evaluation",
                  "4. Real-Time Risk Score Calculation",
                  "5. Verdict: ALLOW / REWRITE / BLOCK",
                  "6. Cryptographic Audit Record Committed",
                ].map((step, idx) => (
                  <div
                    key={step}
                    className="p-2 rounded-lg bg-slate-950/60 border border-white/[0.04] text-slate-300 text-[11px] flex items-center gap-2"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                    {step}
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
