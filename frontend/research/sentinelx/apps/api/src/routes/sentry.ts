import type { FastifyInstance } from "fastify"
import { captureError, captureMessage, addBreadcrumb, startTransaction, healthCheck } from "../lib/sentry"
import { authMiddleware } from "../lib/auth"

export async function registerSentryRoutes(app: FastifyInstance): Promise<void> {
  app.get("/api/sentry/health", { preHandler: authMiddleware }, async () => {
    return healthCheck()
  })

  app.post("/api/sentry/test-error", { preHandler: authMiddleware }, async (request) => {
    try {
      throw new Error("Test error from SentinelX")
    } catch (error) {
      const eventId = captureError(error as Error, { test: true, userId: (request as any).user?.sub })
      return { eventId, message: "Test error captured" }
    }
  })

  app.post("/api/sentry/test-message", { preHandler: authMiddleware }, async () => {
    const eventId = captureMessage("Test message from SentinelX", "info", { test: true })
    return { eventId, message: "Test message captured" }
  })

  app.post("/api/sentry/breadcrumb", { preHandler: authMiddleware }, async (request) => {
    const body = request.body as { category: string; message: string; level?: "debug" | "info" | "warning" | "error"; data?: Record<string, any> }
    addBreadcrumb({
      category: body.category,
      message: body.message,
      level: body.level || "info",
      data: body.data,
      timestamp: Date.now() / 1000,
    })
    return { success: true }
  })

  app.post("/api/sentry/transaction", { preHandler: authMiddleware }, async (request) => {
    const body = request.body as { name: string; op: string; description?: string }
    startTransaction(body.name, body.op)
    return { success: true, transaction: false, note: "Use OpenTelemetry for distributed tracing" }
  })
}