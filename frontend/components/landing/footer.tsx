'use client';

import { ShieldCheck } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-white/[0.08] bg-[#030712] pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 mb-12">
          
          {/* Brand Column */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <span className="font-display font-bold text-lg text-slate-100 tracking-wider">
                AGENT<span className="text-emerald-400">PAY</span>
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-sm leading-relaxed font-sans">
              The AI-native payment security platform combining agent identity, AGENTGUARD policy governance, and FRAUDGUARD risk detection.
            </p>
          </div>

          {/* Column 1: Products */}
          <div>
            <h4 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-widest mb-4">
              Products
            </h4>
            <ul className="space-y-2.5 text-xs font-sans text-slate-400">
              <li><a href="#agentpay" className="hover:text-emerald-400 transition-colors">AgentPay</a></li>
              <li><a href="#agentguard" className="hover:text-emerald-400 transition-colors">AgentGuard</a></li>
              <li><a href="#fraudguard" className="hover:text-emerald-400 transition-colors">FraudGuard</a></li>
              <li><a href="#payments" className="hover:text-emerald-400 transition-colors">Payments</a></li>
            </ul>
          </div>

          {/* Column 2: Resources */}
          <div>
            <h4 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-widest mb-4">
              Resources
            </h4>
            <ul className="space-y-2.5 text-xs font-sans text-slate-400">
              <li><a href="#developers" className="hover:text-emerald-400 transition-colors">Developers</a></li>
              <li><a href="#security" className="hover:text-emerald-400 transition-colors">Security</a></li>
              <li><a href="#documentation" className="hover:text-emerald-400 transition-colors">Documentation</a></li>
              <li><a href="#api" className="hover:text-emerald-400 transition-colors">API Reference</a></li>
            </ul>
          </div>

          {/* Column 3: Platform Status */}
          <div>
            <h4 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-widest mb-4">
              System Status
            </h4>
            <div className="space-y-2.5 text-xs font-mono text-slate-400">
              <div className="flex items-center gap-2 text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>All Systems Operational</span>
              </div>
              <p className="text-[10px] text-slate-500">
                SOC2 Type II Certified · PCI-DSS Level 1
              </p>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-slate-500 gap-4">
          <p>© {new Date().getFullYear()} AGENTPAY Inc. All rights reserved.</p>
          <div className="flex gap-6 text-[11px]">
            <a href="#" className="hover:text-slate-300 transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-slate-300 transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-slate-300 transition-colors">Security Disclosures</a>
          </div>
        </div>

      </div>
    </footer>
  );
}
