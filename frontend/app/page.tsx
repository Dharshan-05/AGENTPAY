'use client';

import { Navbar } from '@/components/landing/navbar';
import { Hero } from '@/components/landing/hero';
import { TrustStrip } from '@/components/landing/trust-strip';
import { Problem } from '@/components/landing/problem';
import { Architecture } from '@/components/landing/architecture';
import { AgentGuardSection } from '@/components/landing/agentguard-section';
import { FraudGuardSection } from '@/components/landing/fraudguard-section';
import { PaymentsSection } from '@/components/landing/payments-section';
import { HowItWorks } from '@/components/landing/how-it-works';
import { LiveTransaction } from '@/components/landing/live-transaction';
import { SecurityTrust } from '@/components/landing/security-trust';
import { FinalCta } from '@/components/landing/final-cta';
import { Footer } from '@/components/landing/footer';
import { GradientMesh } from '@/components/motion/gradient-mesh';
import { CursorFollower } from '@/components/motion/cursor-follower';

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-[#030712] text-slate-100 overflow-hidden font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      
      {/* Background Mesh */}
      <div className="fixed inset-0 pointer-events-none -z-10">
        <div className="absolute inset-0 bg-[#030712]" />
        <GradientMesh colors={['#10B981', '#3B82F6', '#6366F1']} intensity={0.03} />
      </div>

      <CursorFollower />

      {/* 1. Header Navigation */}
      <Navbar />

      {/* 2. Hero Section */}
      <Hero />

      {/* 3. Trust Layer Marquee */}
      <TrustStrip />

      {/* 4. Autonomous Commerce Problem */}
      <Problem />

      {/* 5. AGENTPAY Architecture Pillars */}
      <Architecture />

      {/* 6. AGENTGUARD Policy Governance Deep-Dive */}
      <AgentGuardSection />

      {/* 7. FRAUDGUARD AI Risk Intelligence Deep-Dive */}
      <FraudGuardSection />

      {/* 8. Secure Payment Execution Rails */}
      <PaymentsSection />

      {/* 9. How It Works Step Inspector */}
      <HowItWorks />

      {/* 10. Live Transaction Sandbox */}
      <LiveTransaction />

      {/* 11. Security & Cryptographic Compliance */}
      <SecurityTrust />

      {/* 12. Final CTA & Conversion */}
      <FinalCta />

      {/* 13. Footer */}
      <Footer />

    </div>
  );
}
