'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ShieldCheck, Menu, X, ArrowRight } from 'lucide-react';
import { Magnetic } from '@/components/motion/magnetic';

const NAV_LINKS = [
  { name: 'Product', href: '#product' },
  { name: 'AgentGuard', href: '#agentguard' },
  { name: 'FraudGuard', href: '#fraudguard' },
  { name: 'Payments', href: '#payments' },
  { name: 'Developers', href: '#developers' },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 20);
    }
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-[#030712]/80 backdrop-blur-xl border-b border-white/[0.08] py-3.5 shadow-2xl'
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400/20 to-blue-500/20 border border-emerald-500/30 flex items-center justify-center group-hover:border-emerald-400/60 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <ShieldCheck className="w-5 h-5 text-emerald-400 group-hover:scale-105 transition-transform" />
          </div>
          <div className="flex flex-col">
            <span className="font-display font-bold text-lg tracking-wider text-slate-100 flex items-center gap-1.5">
              AGENT<span className="text-emerald-400">PAY</span>
            </span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <nav className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.name}
              href={link.href}
              className="text-xs font-mono tracking-wider text-slate-300 hover:text-emerald-400 transition-colors uppercase"
            >
              {link.name}
            </a>
          ))}
        </nav>

        {/* Actions */}
        <div className="hidden md:flex items-center gap-4">
          <Link
            href="/login"
            className="text-xs font-mono tracking-wider text-slate-300 hover:text-white px-4 py-2 transition-colors uppercase font-bold"
          >
            Sign In
          </Link>
          <Magnetic strength={10}>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-slate-950 font-semibold text-xs font-mono uppercase tracking-wider shadow-[0_0_20px_rgba(16,185,129,0.25)] hover:shadow-[0_0_30px_rgba(16,185,129,0.4)] transition-all"
            >
              Get Started
              <ArrowRight className="w-3.5 h-3.5 text-slate-950" />
            </Link>
          </Magnetic>
        </div>

        {/* Mobile menu toggle button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden text-slate-300 hover:text-white p-2"
          aria-label="Toggle Navigation"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#090D16]/95 border-b border-white/[0.08] px-6 py-6 space-y-4 backdrop-blur-2xl">
          {NAV_LINKS.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block text-sm font-mono tracking-wider text-slate-300 hover:text-emerald-400 py-1 uppercase"
            >
              {link.name}
            </a>
          ))}
          <div className="pt-4 border-t border-white/[0.06] flex flex-col gap-3">
            <Link
              href="/login"
              className="text-center text-xs font-mono tracking-wider text-slate-300 hover:text-white py-2 uppercase border border-white/10 rounded-xl"
            >
              Sign In
            </Link>
            <Link
              href="/login"
              className="text-center text-xs font-mono uppercase tracking-wider font-semibold py-3 rounded-xl bg-emerald-500 text-slate-950 shadow-[0_0_20px_rgba(16,185,129,0.3)]"
            >
              Get Started
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
