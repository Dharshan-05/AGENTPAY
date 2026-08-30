import type { FastifyInstance } from "fastify"
import {
  sendEmail,
  sendSlackMessage,
  healthCheck,
  createIncidentAlertEmail,
  createWeeklyComplianceReportEmail,
  createBillingNotificationEmail,
  createSlackIncidentAlert,
  createSlackWeeklyReport,
  isResendConfigured,
  isSlackConfigured,
} from "../lib/notifications"
import { authMiddleware } from "../lib/auth"

export async function registerNotificationRoutes(app: FastifyInstance): Promise<void> {
  app.get("/api/notifications/health", { preHandler: authMiddleware }, async () => {
    return healthCheck()
  })

  app.post("/api/notifications/test-email", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as { to?: string; subject?: string; html?: string; text?: string }

    const result = await sendEmail({
      to: body.to || (request as any).user?.email || "test@sentinelx.dev",
      subject: body.subject || "[SentinelX] Test Email",
      html: body.html || "<p>This is a test email from SentinelX.</p>",
      text: body.text || "This is a test email from SentinelX.",
    })

    if (!result.success) {
      return reply.code(500).send({ error: result.error })
    }

    return result
  })

  app.post("/api/notifications/test-slack", { preHandler: authMiddleware }, async (_request, reply) => {
    const result = await sendSlackMessage({
      text: "Test message from SentinelX",
      blocks: [
        {
          type: "header",
          text: { type: "plain_text", text: "🧪 SentinelX Test Message", emoji: true },
        },
        {
          type: "section",
          text: { type: "mrkdwn", text: "This is a test message from SentinelX notification system." },
        },
      ],
    })

    if (!result.success) {
      return reply.code(500).send({ error: result.error })
    }

    return result
  })

  app.post("/api/notifications/incident-alert", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      incident: {
        id: string
        severity: string
        title: string
        description: string
        riskScore: number
        user: { name: string; email: string; department: string }
        createdAt: string
      }
      recipients?: string[]
      sendSlack?: boolean
    }

    if (!body?.incident || typeof body.incident !== "object") {
      return reply.code(400).send({ error: "incident object is required" })
    }
    if (!body.incident.id || !body.incident.severity) {
      return reply.code(400).send({ error: "incident.id and incident.severity are required" })
    }

    const emailResult = await sendEmail({
      to: body.recipients || [(request as any).user?.email || "security@sentinelx.dev"],
      ...createIncidentAlertEmail(body.incident),
    })

    let slackResult = { success: true }
    if (body.sendSlack !== false) {
      slackResult = await sendSlackMessage(createSlackIncidentAlert(body.incident))
    }

    if (!emailResult.success || !slackResult.success) {
      return reply.code(500).send({
        error: "Failed to send notifications",
        email: emailResult,
        slack: slackResult,
      })
    }

    return { email: emailResult, slack: slackResult }
  })

  app.post("/api/notifications/weekly-report", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      report: {
        period: string
        complianceScore: number
        totalEvents: number
        threatsBlocked: number
        threatsRewritten: number
        topViolations: Array<{ regulation: string; count: number }>
        topDepartments: Array<{ department: string; riskIndex: number }>
      }
      recipients?: string[]
      sendSlack?: boolean
    }

    const emailResult = await sendEmail({
      to: body.recipients || [(request as any).user?.email || "compliance@sentinelx.dev"],
      ...createWeeklyComplianceReportEmail(body.report),
    })

    let slackResult = { success: true }
    if (body.sendSlack !== false) {
      slackResult = await sendSlackMessage(createSlackWeeklyReport({
        period: body.report.period,
        complianceScore: body.report.complianceScore,
        totalEvents: body.report.totalEvents,
        threatsBlocked: body.report.threatsBlocked,
        threatsRewritten: body.report.threatsRewritten,
      }))
    }

    if (!emailResult.success || !slackResult.success) {
      return reply.code(500).send({
        error: "Failed to send notifications",
        email: emailResult,
        slack: slackResult,
      })
    }

    return { email: emailResult, slack: slackResult }
  })

  app.post("/api/notifications/billing", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      notification: {
        type: "invoice_paid" | "invoice_failed" | "subscription_renewing" | "subscription_cancelled" | "payment_method_expiring"
        customerName: string
        amount?: number
        currency?: string
        invoiceUrl?: string
        subscriptionUrl?: string
      }
      to?: string
    }

    const emailResult = await sendEmail({
      to: body.to || (request as any).user?.email || "billing@sentinelx.dev",
      ...createBillingNotificationEmail(body.notification),
    })

    if (!emailResult.success) {
      return reply.code(500).send({ error: "Failed to send billing notification", email: emailResult })
    }

    return { email: emailResult }
  })

  app.get("/api/notifications/config", { preHandler: authMiddleware }, async () => {
    return {
      resend: { configured: isResendConfigured() },
      slack: { configured: isSlackConfigured() },
    }
  })
}