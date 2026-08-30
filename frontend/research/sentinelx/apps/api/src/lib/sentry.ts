import * as Sentry from "@sentry/node"
import { nodeProfilingIntegration } from "@sentry/profiling-node"

const SENTRY_DSN = process.env.SENTRY_DSN
const SENTRY_ENV = process.env.SENTRY_ENVIRONMENT || process.env.NODE_ENV || "development"
const SENTRY_RELEASE = process.env.SENTRY_RELEASE || "sentinelx@1.0.0"

let initialized = false

export function initSentry(): void {
  if (!SENTRY_DSN) {
    console.log("[Sentry] DSN not set — running without error tracking")
    return
  }

  if (initialized) return

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: SENTRY_ENV,
    release: SENTRY_RELEASE,
    tracesSampleRate: 1.0,
    profilesSampleRate: 1.0,
    integrations: [
      nodeProfilingIntegration(),
      Sentry.httpIntegration(),
      Sentry.consoleIntegration(),
    ],
    beforeSend(event) {
      // Filter out health check noise
      if (event.request?.url?.includes("/api/health")) {
        return null
      }
      return event
    },
  })

  initialized = true
  console.log("[Sentry] Initialized")
}

export function captureError(error: Error, context?: Record<string, any>): string {
  return Sentry.captureException(error, { extra: context })
}

export function captureMessage(message: string, level: Sentry.SeverityLevel = "info", context?: Record<string, any>): string {
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
  // startTransaction not available in this version of @sentry/node
  // Use OpenTelemetry for distributed tracing instead
  return undefined
}

export function getSentry(): typeof Sentry {
  return Sentry
}

export function isSentryInitialized(): boolean {
  return initialized
}

export function healthCheck(): { initialized: boolean; dsnConfigured: boolean } {
  return { initialized, dsnConfigured: !!SENTRY_DSN }
}