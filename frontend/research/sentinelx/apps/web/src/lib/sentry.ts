import * as Sentry from "@sentry/nextjs"

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN
const SENTRY_ENV = process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || process.env.NODE_ENV || "development"
const SENTRY_RELEASE = process.env.NEXT_PUBLIC_SENTRY_RELEASE || "sentinelx-web@1.0.0"

export function initSentry(): void {
  if (!SENTRY_DSN) {
    console.log("[Sentry] Web DSN not set — running without error tracking")
    return
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: SENTRY_ENV,
    release: SENTRY_RELEASE,
    tracesSampleRate: 1.0,
    replaysOnErrorSampleRate: 1.0,
    replaysSessionSampleRate: 0.1,
    integrations: [
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
      Sentry.browserTracingIntegration(),
    ],
    beforeSend(event) {
      // Filter out development noise
      if (event.request?.url?.includes("/api/auth/")) {
        return null
      }
      return event
    },
  })

  console.log("[Sentry] Web initialized")
}

export function captureError(error: Error, context?: Record<string, any>): string {
  return Sentry.captureException(error, { extra: context })
}

export function captureMessage(message: string, level: "info" | "warning" | "error" = "info", context?: Record<string, any>): string {
  return Sentry.captureMessage(message, { level, extra: context })
}

export function setUserContext(user: { id: string; email: string; role: string } | null): void {
  if (user) {
    Sentry.setUser({ id: user.id, email: user.email, role: user.role })
  } else {
    Sentry.setUser(null)
  }
}

export function addBreadcrumb(breadcrumb: Sentry.Breadcrumb): void {
  Sentry.addBreadcrumb(breadcrumb)
}

export function startTransaction(_name: string, _op: string): undefined {
  // startTransaction not available in this version of @sentry/nextjs
  // Use Sentry.startInactiveSpan or OpenTelemetry for tracing
  return undefined
}

export function healthCheck(): { initialized: boolean; dsnConfigured: boolean } {
  return { initialized: !!SENTRY_DSN, dsnConfigured: !!SENTRY_DSN }
}