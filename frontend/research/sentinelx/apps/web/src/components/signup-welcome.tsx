"use client"

import { Sparkles, AlertCircle } from "lucide-react"

interface SignupWelcomeBannerProps {
  show: boolean
}

export function SignupWelcomeBanner({ show }: SignupWelcomeBannerProps) {
  if (!show) return null

  return (
    <div className="mb-6 p-4 rounded-xl bg-status-low/10 border border-status-low/20 animate-in slide-in-from-top-4 duration-300">
      <div className="flex items-center justify-center gap-2 text-status-low">
        <Sparkles className="h-5 w-5" />
        <span className="font-medium">Welcome to SentinelX!</span>
        <AlertCircle className="h-5 w-5" />
      </div>
      <p className="mt-2 text-sm text-text-secondary">
        Your account has been created. Choose a plan to activate your subscription and start protecting your AI workflows.
      </p>
    </div>
  )
}