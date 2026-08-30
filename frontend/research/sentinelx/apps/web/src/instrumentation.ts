import * as Sentry from "@sentry/nextjs"

export function register() {
  if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    Sentry.init({
      dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
      environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT || process.env.NODE_ENV || "development",
      release: process.env.NEXT_PUBLIC_SENTRY_RELEASE || "sentinelx-web@1.0.0",
      tracesSampleRate: 1.0,
      debug: process.env.NODE_ENV === "development",
    })
  }
}