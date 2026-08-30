"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Shield, AlertCircle, Eye, EyeOff, ArrowLeft } from "lucide-react"
import { signIn } from "next-auth/react"
import { cn } from "@/lib/utils"

export default function SignupPage() {
  const router = useRouter()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    
    if (!name.trim() || !email.trim() || !password || !confirmPassword) {
      setError("All fields are required")
      return
    }
    
    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }
    
    if (password.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }
    
    setLoading(true)
    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        setError(data.error || "Signup failed")
        setLoading(false)
        return
      }
      
      // Sign in with credentials after signup
      const result = await signIn("email-password", {
        email,
        password,
        redirect: false,
      })
      
      if (result?.error) {
        setError("Account created but sign in failed. Please sign in manually.")
        setLoading(false)
        return
      }
      
      // Redirect to pricing page to select a plan
      router.push("/pricing?signup=true")
    } catch {
      setError("An unexpected error occurred")
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
            Create your account
          </h1>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-text-muted">
            Join 500+ organizations protecting their data with SentinelX AI Governance Firewall.
          </p>
          <ul className="mt-10 space-y-3">
            {["Real-time threat detection", "Role-based access control", "Compliance automation", "Immutable audit trail"].map((item) => (
              <li key={item} className="flex items-center gap-2.5 text-sm text-text-secondary">
                <svg className="h-4 w-4 text-accent-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
                {item}
              </li>
            ))}
          </ul>
        </div>
        <p className="relative text-[11px] text-text-muted">
          SOC 2 Type II · GDPR · SAML 2.0 · OIDC — &copy; {new Date().getFullYear()} SentinelX
        </p>
      </div>

      {/* Right: sign-up card */}
      <div className="flex w-full items-center justify-center px-6 py-12 lg:w-1/2">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2.5 lg:hidden">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent/15">
              <Shield className="h-4.5 w-4.5 text-accent-light" />
            </div>
            <span className="text-sm font-semibold tracking-tight text-text-primary">SentinelX</span>
          </div>

          <div className="flex items-center gap-2 mb-8">
            <button
              onClick={() => router.push("/login")}
              className="flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to login
            </button>
          </div>

          <h2 className="text-xl font-semibold tracking-tight text-text-primary">Create your account</h2>
          <p className="mt-1.5 text-sm text-text-muted">Enter your details to get started.</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <div>
              <label htmlFor="name" className="mb-1.5 block text-xs font-medium text-text-secondary">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                className={cn(
                  "w-full rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent",
                  error && "border-status-critical"
                )}
                disabled={loading}
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="mb-1.5 block text-xs font-medium text-text-secondary">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@company.com"
                className={cn(
                  "w-full rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent",
                  error && "border-status-critical"
                )}
                disabled={loading}
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="mb-1.5 block text-xs font-medium text-text-secondary">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className={cn(
                    "w-full rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent pr-10",
                    error && "border-status-critical"
                  )}
                  disabled={loading}
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <p className="mt-1 text-[11px] text-text-muted">Must be at least 8 characters</p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="mb-1.5 block text-xs font-medium text-text-secondary">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type={showPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className={cn(
                  "w-full rounded-lg border border-border-default bg-white/[0.03] px-3 py-2 text-sm text-text-primary placeholder:text-text-muted focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent",
                  error && "border-status-critical"
                )}
                disabled={loading}
                required
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-lg border border-status-critical/30 bg-status-critical/10 px-3 py-2 text-xs text-status-critical">
                <AlertCircle className="h-3.5 w-3.5" />
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-semibold text-bg-primary transition-colors hover:bg-accent-light disabled:opacity-60"
            >
              {loading ? (
                <>
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle className="opacity-25" cx="12" cy="12" r="10" strokeWidth="4" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 2v4m0 12v4M2 12h4m12 0h4" />
                  </svg>
                  Creating account...
                </>
              ) : (
                "Create account"
              )}
            </button>

            <p className="text-center text-[11px] text-text-muted">
              By creating an account, you agree to our{" "}
              <a href="/legal/terms" className="text-accent-light hover:underline">Terms of Service</a>
              {" and "}
              <a href="/legal/privacy" className="text-accent-light hover:underline">Privacy Policy</a>
            </p>
          </form>

          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border-subtle" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-bg-page px-2 text-text-muted">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              <button
                type="button"
                disabled={loading}
                className="flex w-full items-center justify-center gap-3 rounded-lg border border-border-default bg-white px-4 py-2.5 text-sm font-medium text-zinc-900 transition-all hover:border-border-strong hover:shadow-sm disabled:opacity-60"
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                Continue with Google
              </button>

              <button
                type="button"
                onClick={() => window.location.href = "/login?demo=true"}
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-lg border border-border-subtle bg-white/[0.01] px-4 py-2.5 text-xs font-medium text-text-secondary transition-colors hover:bg-white/[0.04] disabled:opacity-60"
              >
                <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect width="18" height="18" x="3" y="3" rx="2" />
                  <path d="M7 9h10M7 13h10M7 17h10" />
                </svg>
                Try demo (no account needed)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}