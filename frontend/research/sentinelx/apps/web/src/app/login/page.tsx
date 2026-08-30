"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Shield, ArrowRight, AlertCircle, Loader2, ChevronDown, Lock, CheckCircle2 } from "lucide-react"
import { useAuth } from "@/lib/auth"
import { ROLES } from "@/lib/rbac"

const GOOGLE_CONFIGURED = Boolean(process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID)

const DEMO_USERS = [
  { email: "admin@sentinelx.dev", role: "super-admin" },
  { email: "analyst@sentinelx.dev", role: "soc-analyst" },
  { email: "officer@sentinelx.dev", role: "compliance-officer" },
  { email: "manager@sentinelx.dev", role: "engineering-manager" },
  { email: "employee@sentinelx.dev", role: "employee" },
  { email: "auditor@sentinelx.dev", role: "auditor" },
].map((u) => ({ ...u, roleDef: ROLES.find((r) => r.id === u.role) }))

export default function LoginPage() {
  const { loginWithGoogle, loginWithDemo } = useAuth()
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [showDemo, setShowDemo] = useState(false)
  const [demoEmail, setDemoEmail] = useState(DEMO_USERS[0].email)

  const handleGoogle = async () => {
    setLoading(true)
    setError("")
    try {
      await loginWithGoogle()
    } catch {
      setError("Could not start Google sign-in. Please try again.")
      setLoading(false)
    }
  }

  const handleDemo = async () => {
    setLoading(true)
    setError("")
    try {
      await loginWithDemo(demoEmail)
      const landing = DEMO_USERS.find((u) => u.email === demoEmail)?.roleDef?.landing ?? "/dashboard"
      router.push(landing)
    } catch {
      setError("Demo login failed")
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-bg-page">
      {/* Left: brand panel */}
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-bg-secondary/40 p-12 lg:flex">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(11,130,122,0.15),transparent_55%)]" />
        <div className="relative">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15">
              <Shield className="h-5 w-5 text-accent-light" />
            </div>
            <span className="text-base font-semibold tracking-tight text-text-primary">SentinelX</span>
          </div>
          <h1 className="mt-16 max-w-md text-3xl font-semibold leading-tight tracking-tight text-text-primary">
            Enterprise AI governance firewall
          </h1>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-text-muted">
            Detect, prevent, explain, and audit sensitive data leakage to large language models in real time.
          </p>
          <ul className="mt-10 space-y-3">
            {["Real-time detection pipeline", "Role-based access control", "Immutable audit trail"].map((item) => (
              <li key={item} className="flex items-center gap-2.5 text-sm text-text-secondary">
                <CheckCircle2 className="h-4 w-4 text-accent-light" />
                {item}
              </li>
            ))}
          </ul>
        </div>
        <p className="relative text-[11px] text-text-muted">
          SOC 2 Type II · GDPR · SAML 2.0 · OIDC — &copy; {new Date().getFullYear()} SentinelX
        </p>
      </div>

      {/* Right: sign-in card */}
      <div className="flex w-full items-center justify-center px-6 py-12 lg:w-1/2">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/15">
              <Shield className="h-4.5 w-4.5 text-accent-light" />
            </div>
            <span className="text-sm font-semibold tracking-tight text-text-primary">SentinelX</span>
          </div>

          <h2 className="text-xl font-semibold tracking-tight text-text-primary">Sign in to SentinelX</h2>
          <p className="mt-1.5 text-sm text-text-muted">Use your Google account to continue.</p>

          <div className="mt-8 space-y-3">
            {!GOOGLE_CONFIGURED && (
              <div className="flex items-start gap-2.5 rounded-lg border border-border-default bg-white/[0.02] px-3.5 py-3">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-text-muted" />
                <div>
                  <p className="text-xs font-medium text-text-primary">Google OAuth not configured</p>
                  <p className="mt-0.5 text-[11px] leading-relaxed text-text-muted">
                    Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to enable Google sign-in. Demo login below remains available.
                  </p>
                </div>
              </div>
            )}

            {GOOGLE_CONFIGURED && (
              <button
                onClick={handleGoogle}
                disabled={loading}
                className="flex w-full items-center justify-center gap-3 rounded-lg border border-border-default bg-white px-4 py-2.5 text-sm font-medium text-zinc-900 transition-all hover:border-border-strong hover:shadow-sm disabled:opacity-60"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <svg className="h-5 w-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                )}
                Continue with Google
              </button>
            )}

            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-border-subtle" />
              <span className="text-[10px] uppercase tracking-wider text-text-muted">or</span>
              <div className="h-px flex-1 bg-border-subtle" />
            </div>

            <button
              onClick={() => setShowDemo((s) => !s)}
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-border-subtle bg-white/[0.01] px-4 py-2.5 text-xs font-medium text-text-secondary transition-colors hover:bg-white/[0.04]"
            >
              <Lock className="h-3.5 w-3.5" />
              Demo login
              <ChevronDown className={`h-3.5 w-3.5 transition-transform ${showDemo ? "rotate-180" : ""}`} />
            </button>

            {showDemo && (
              <div className="space-y-2.5 rounded-lg border border-border-default bg-white/[0.02] p-3.5">
                <select
                  aria-label="Demo user role"
                  value={demoEmail}
                  onChange={(e) => setDemoEmail(e.target.value)}
                  className="w-full rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-xs text-text-primary focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
                >
                  {DEMO_USERS.map((u) => (
                    <option key={u.email} value={u.email}>
                      {u.roleDef?.label ?? u.role} — {u.email}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleDemo}
                  disabled={loading}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent/20 px-4 py-2 text-xs font-semibold text-accent-light transition-colors hover:bg-accent/30 disabled:opacity-60"
                >
                  {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <ArrowRight className="h-3.5 w-3.5" />}
                  Enter demo
                </button>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-2 rounded-lg border border-status-critical/30 bg-status-critical/10 px-3 py-2 text-xs text-status-critical">
                <AlertCircle className="h-3.5 w-3.5" />
                {error}
              </div>
            )}
          </div>

          <p className="mt-8 text-center text-[10px] leading-relaxed text-text-muted">
            Protected by enterprise SSO · MFA enforced · Session secured with httpOnly cookies
          </p>
          <p className="mt-6 text-center text-sm text-text-muted">
            Don't have an account?{" "}
            <a href="/signup" className="text-accent-light hover:underline font-medium">
              Create an account
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}