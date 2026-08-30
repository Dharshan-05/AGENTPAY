import { Resend } from "resend"

const RESEND_API_KEY = process.env.RESEND_API_KEY
const FROM_EMAIL = process.env.FROM_EMAIL || "SentinelX <noreply@sentinelx.dev>"
const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL

let resend: Resend | null = null
let resendConfigured = false
let slackConfigured = false

if (RESEND_API_KEY) {
  resend = new Resend(RESEND_API_KEY)
  resendConfigured = true
  console.log("[Resend] Configured")
} else {
  console.log("[Resend] Not configured — running in demo mode")
}

if (SLACK_WEBHOOK_URL) {
  slackConfigured = true
  console.log("[Slack] Webhook configured")
} else {
  console.log("[Slack] Webhook not configured — running in demo mode")
}

export interface EmailOptions {
  to: string | string[]
  subject: string
  html?: string
  text?: string
  from?: string
  tags?: Array<{ name: string; value: string }>
}

export interface SlackMessage {
  text?: string
  blocks?: Array<{
    type: string
    text?: { type: string; text: string; emoji?: boolean }
    fields?: Array<{ type: string; text: string; verbatim?: boolean }>
    accessory?: { type: string; image_url: string; alt_text: string }
    elements?: Array<{ type: string; text?: { type: string; text: string; emoji?: boolean }; style?: string; url?: string }>
  }>
  attachments?: Array<{
    color: string
    title: string
    text: string
    fields?: Array<{ title: string; value: string; short?: boolean }>
    footer?: string
    ts?: number
  }>
}

export async function sendEmail(options: EmailOptions): Promise<{ id: string | null; success: boolean; error?: string }> {
  if (!resendConfigured || !resend) {
    console.log("[Resend] Demo mode - email would be sent:", { to: options.to, subject: options.subject })
    return { id: `demo_${Date.now()}`, success: true }
  }

  try {
    const result = await resend.emails.send({
      from: options.from || FROM_EMAIL,
      to: Array.isArray(options.to) ? options.to : [options.to],
      subject: options.subject,
      html: options.html,
      text: options.text,
    } as any)
    return { id: result.data?.id ?? null, success: true }
  } catch (error) {
    console.error("[Resend] Send failed:", error)
    return { id: null, success: false, error: String(error) }
  }
}

export async function sendSlackMessage(message: SlackMessage): Promise<{ success: boolean; error?: string }> {
  if (!slackConfigured || !SLACK_WEBHOOK_URL) {
    console.log("[Slack] Demo mode - message would be sent:", message)
    return { success: true }
  }

  try {
    const response = await fetch(SLACK_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message),
    })
    if (!response.ok) {
      throw new Error(`Slack webhook failed: ${response.status}`)
    }
    return { success: true }
  } catch (error) {
    console.error("[Slack] Send failed:", error)
    return { success: false, error: String(error) }
  }
}

export function isResendConfigured(): boolean {
  return resendConfigured
}

export function isSlackConfigured(): boolean {
  return slackConfigured
}

export function healthCheck(): { resend: { configured: boolean }; slack: { configured: boolean } } {
  return { resend: { configured: resendConfigured }, slack: { configured: slackConfigured } }
}

// Template functions for common SentinelX emails
export function createIncidentAlertEmail(incident: {
  id: string
  severity: string
  title: string
  description: string
  riskScore: number
  user: { name: string; email: string; department: string }
  createdAt: string
}): { subject: string; html: string; text: string } {
  const severityColors: Record<string, string> = {
    CRITICAL: "#dc2626",
    HIGH: "#ea580c",
    MEDIUM: "#f59e0b",
    LOW: "#10b981",
  }
  const color = severityColors[incident.severity] || "#6b7280"

  const subject = `[SentinelX] ${incident.severity} Incident: ${incident.title}`
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">
      <div style="background: linear-gradient(135deg, #0f766e 0%, #0d5c56 100%); padding: 24px; border-radius: 12px 12px 0 0;">
        <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 600;">SentinelX Security Alert</h1>
      </div>
      <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
        <div style="display: inline-block; background: ${color}; color: white; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px;">
          ${incident.severity}
        </div>
        <h2 style="margin: 0 0 16px; font-size: 20px; color: #111827;">${incident.title}</h2>
        <p style="margin: 0 0 24px; color: #4b5563;">${incident.description}</p>
        
        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 24px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
              <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Incident ID</td>
              <td style="padding: 8px 0; font-weight: 600; font-family: monospace; font-size: 13px;">${incident.id}</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Risk Score</td>
              <td style="padding: 8px 0; font-weight: 600; color: ${color};">${incident.riskScore}/100</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">User</td>
              <td style="padding: 8px 0; font-weight: 600;">${incident.user.name} (${incident.user.department})</td>
            </tr>
            <tr>
              <td style="padding: 8px 0; color: #6b7280; font-size: 14px;">Detected</td>
              <td style="padding: 8px 0; font-weight: 600;">${new Date(incident.createdAt).toLocaleString()}</td>
            </tr>
          </table>
        </div>
        
        <a href="${process.env.NEXT_PUBLIC_APP_URL}/incidents/${incident.id}" style="display: inline-block; background: #0f766e; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
          View Incident in SentinelX
        </a>
        
        <p style="margin-top: 24px; font-size: 12px; color: #9ca3af;">
          This alert was generated by SentinelX AI Governance Firewall. 
          <a href="${process.env.NEXT_PUBLIC_APP_URL}/settings/notifications" style="color: #0f766e;">Manage notification preferences</a>
        </p>
      </div>
    </body>
    </html>
  `
  const text = `
SentinelX Security Alert - ${incident.severity}

${incident.title}
${incident.description}

Incident ID: ${incident.id}
Risk Score: ${incident.riskScore}/100
User: ${incident.user.name} (${incident.user.department})
Detected: ${new Date(incident.createdAt).toLocaleString()}

View incident: ${process.env.NEXT_PUBLIC_APP_URL}/incidents/${incident.id}
  `
  return { subject, html, text }
}

export function createWeeklyComplianceReportEmail(report: {
  period: string
  complianceScore: number
  totalEvents: number
  threatsBlocked: number
  threatsRewritten: number
  topViolations: Array<{ regulation: string; count: number }>
  topDepartments: Array<{ department: string; riskIndex: number }>
}): { subject: string; html: string; text: string } {
  const subject = `[SentinelX] Weekly Compliance Report - ${report.period}`
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">
      <div style="background: linear-gradient(135deg, #0f766e 0%, #0d5c56 100%); padding: 24px; border-radius: 12px 12px 0 0;">
        <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 600;">Weekly Compliance Report</h1>
        <p style="margin: 8px 0 0; color: rgba(255,255,255,0.8);">${report.period}</p>
      </div>
      <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 24px; margin-bottom: 24px; text-align: center;">
          <p style="margin: 0 0 8px; color: #6b7280; font-size: 14px;">Compliance Score</p>
          <p style="margin: 0; font-size: 48px; font-weight: 700; color: ${report.complianceScore >= 85 ? "#10b981" : report.complianceScore >= 70 ? "#f59e0b" : "#dc2626"};">
            ${report.complianceScore}%
          </p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
          <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; text-align: center;">
            <p style="margin: 0 0 4px; color: #6b7280; font-size: 13px;">Total Events</p>
            <p style="margin: 0; font-size: 24px; font-weight: 700; color: #111827;">${report.totalEvents.toLocaleString()}</p>
          </div>
          <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; text-align: center;">
            <p style="margin: 0 0 4px; color: #6b7280; font-size: 13px;">Threats Blocked</p>
            <p style="margin: 0; font-size: 24px; font-weight: 700; color: #dc2626;">${report.threatsBlocked}</p>
          </div>
          <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; text-align: center;">
            <p style="margin: 0 0 4px; color: #6b7280; font-size: 13px;">Threats Rewritten</p>
            <p style="margin: 0; font-size: 24px; font-weight: 700; color: #ea580c;">${report.threatsRewritten}</p>
          </div>
          <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; text-align: center;">
            <p style="margin: 0 0 4px; color: #6b7280; font-size: 13px;">Threats Allowed</p>
            <p style="margin: 0; font-size: 24px; font-weight: 700; color: #10b981;">${report.totalEvents - report.threatsBlocked - report.threatsRewritten}</p>
          </div>
        </div>
        
        ${report.topViolations.length > 0 && `
          <div style="margin-bottom: 24px;">
            <h3 style="margin: 0 0 16px; font-size: 16px; color: #111827;">Top Violations</h3>
            <table style="width: 100%; border-collapse: collapse;">
              <thead>
                <tr style="border-bottom: 2px solid #e5e7eb;">
                  <th style="padding: 12px; text-align: left; color: #6b7280; font-size: 13px; font-weight: 600;">Regulation</th>
                  <th style="padding: 12px; text-align: right; color: #6b7280; font-size: 13px; font-weight: 600;">Count</th>
                </tr>
              </thead>
              <tbody>
                ${report.topViolations.map(v => `
                  <tr style="border-bottom: 1px solid #f3f4f6;">
                    <td style="padding: 12px; font-size: 14px;">${v.regulation}</td>
                    <td style="padding: 12px; text-align: right; font-weight: 600;">${v.count}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        `}
        
        <a href="${process.env.NEXT_PUBLIC_APP_URL}/compliance" style="display: inline-block; background: #0f766e; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
          View Full Report in SentinelX
        </a>
        
        <p style="margin-top: 24px; font-size: 12px; color: #9ca3af;">
          This report was generated by SentinelX AI Governance Firewall.
        </p>
      </div>
    </body>
    </html>
  `
  const text = `
SentinelX Weekly Compliance Report - ${report.period}

Compliance Score: ${report.complianceScore}%
Total Events: ${report.totalEvents}
Threats Blocked: ${report.threatsBlocked}
Threats Rewritten: ${report.threatsRewritten}

Top Violations:
${report.topViolations.map(v => `  ${v.regulation}: ${v.count}`).join("\n")}

View full report: ${process.env.NEXT_PUBLIC_APP_URL}/compliance
  `
  return { subject, html, text }
}

export function createBillingNotificationEmail(notification: {
  type: "invoice_paid" | "invoice_failed" | "subscription_renewing" | "subscription_cancelled" | "payment_method_expiring"
  customerName: string
  amount?: number
  currency?: string
  invoiceUrl?: string
  subscriptionUrl?: string
}): { subject: string; html: string; text: string } {
  const templates: Record<string, { subject: string; title: string; message: string; ctaText: string; ctaUrl: string }> = {
    invoice_paid: {
      subject: "[SentinelX] Invoice Paid",
      title: "Payment Received",
      message: "Thank you for your payment. Your invoice has been paid successfully.",
      ctaText: "View Invoice",
      ctaUrl: notification.invoiceUrl || "",
    },
    invoice_failed: {
      subject: "[SentinelX] Payment Failed",
      title: "Payment Failed",
      message: "We were unable to process your payment. Please update your payment method to avoid service interruption.",
      ctaText: "Update Payment Method",
      ctaUrl: notification.subscriptionUrl || "",
    },
    subscription_renewing: {
      subject: "[SentinelX] Subscription Renewing Soon",
      title: "Subscription Renewal",
      message: "Your subscription will renew soon. No action is needed unless you wish to make changes.",
      ctaText: "Manage Subscription",
      ctaUrl: notification.subscriptionUrl || "",
    },
    subscription_cancelled: {
      subject: "[SentinelX] Subscription Cancelled",
      title: "Subscription Cancelled",
      message: "Your subscription has been cancelled. You'll continue to have access until the end of your billing period.",
      ctaText: "Reactivate",
      ctaUrl: notification.subscriptionUrl || "",
    },
    payment_method_expiring: {
      subject: "[SentinelX] Payment Method Expiring",
      title: "Payment Method Expiring",
      message: "Your payment method is about to expire. Please update it to ensure uninterrupted service.",
      ctaText: "Update Payment Method",
      ctaUrl: notification.subscriptionUrl || "",
    },
  }

  const t = templates[notification.type]
  const subject = t.subject
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; max-width: 600px; margin: 0 auto; padding: 20px;">
      <div style="background: linear-gradient(135deg, #0f766e 0%, #0d5c56 100%); padding: 24px; border-radius: 12px 12px 0 0;">
        <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 600;">SentinelX Billing</h1>
      </div>
      <div style="background: #f9fafb; padding: 24px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 12px 12px;">
        <h2 style="margin: 0 0 16px; font-size: 20px; color: #111827;">${t.title}</h2>
        <p style="margin: 0 0 24px; color: #4b5563;">Hi ${notification.customerName}, ${t.message}</p>
        ${notification.amount && `
          <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 24px; text-align: center;">
            <p style="margin: 0 0 4px; color: #6b7280; font-size: 13px;">Amount</p>
            <p style="margin: 0; font-size: 24px; font-weight: 700; color: #111827;">${notification.currency} ${(notification.amount / 100).toLocaleString()}</p>
          </div>
        `}
        ${t.ctaUrl && `
          <a href="${t.ctaUrl}" style="display: inline-block; background: #0f766e; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
            ${t.ctaText}
          </a>
        `}
        <p style="margin-top: 24px; font-size: 12px; color: #9ca3af;">
          This notification was sent by SentinelX AI Governance Firewall.
        </p>
      </div>
    </body>
    </html>
  `
  const text = `
SentinelX Billing - ${t.title}

Hi ${notification.customerName},

${t.message}

${notification.amount ? `Amount: ${notification.currency} ${(notification.amount / 100).toLocaleString()}` : ""}

${t.ctaUrl ? `Manage: ${t.ctaUrl}` : ""}
  `
  return { subject, html, text }
}

export function createSlackIncidentAlert(incident: {
  id: string
  severity: string
  title: string
  description: string
  riskScore: number
  user: { name: string; email: string; department: string }
  createdAt: string
}): SlackMessage {
  const severityColors: Record<string, string> = {
    CRITICAL: "#dc2626",
    HIGH: "#ea580c",
    MEDIUM: "#f59e0b",
    LOW: "#10b981",
  }
  const color = severityColors[incident.severity] || "#6b7280"
  const severityEmoji: Record<string, string> = {
    CRITICAL: "🔴",
    HIGH: "🟠",
    MEDIUM: "🟡",
    LOW: "🟢",
  }

  return {
    blocks: [
      {
        type: "header",
        text: { type: "plain_text", text: `${severityEmoji[incident.severity] || "⚠️"} SentinelX: ${incident.severity} Incident`, emoji: true },
      },
      {
        type: "section",
        text: { type: "mrkdwn", text: `*${incident.title}*\n${incident.description}` },
      },
      {
        type: "section",
        fields: [
          { type: "mrkdwn", text: `*Incident ID:*\n\`${incident.id}\``, verbatim: true },
          { type: "mrkdwn", text: `*Risk Score:*\n${incident.riskScore}/100` },
          { type: "mrkdwn", text: `*User:*\n${incident.user.name} (${incident.user.department})` },
          { type: "mrkdwn", text: `*Time:*\n${new Date(incident.createdAt).toLocaleString()}` },
        ],
      },
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: { type: "plain_text", text: "View in SentinelX" },
            style: "primary",
            url: `${process.env.NEXT_PUBLIC_APP_URL}/incidents/${incident.id}`,
          },
        ],
      },
    ],
    attachments: [
      {
        color,
        title: "Incident Details",
        text: `SentinelX AI Governance Firewall detected a ${incident.severity.toLowerCase()} severity incident.`,
        footer: "SentinelX",
        ts: Math.floor(new Date(incident.createdAt).getTime() / 1000),
      },
    ],
  }
}

export function createSlackWeeklyReport(report: {
  period: string
  complianceScore: number
  totalEvents: number
  threatsBlocked: number
  threatsRewritten: number
}): SlackMessage {
  return {
    blocks: [
      {
        type: "header",
        text: { type: "plain_text", text: "📊 SentinelX Weekly Compliance Report", emoji: true },
      },
      {
        type: "section",
        text: { type: "mrkdwn", text: `*Period:* ${report.period}\n*Compliance Score:* ${report.complianceScore}%` },
        accessory: {
          type: "image",
          image_url: "https://cdn.jsdelivr.net/gh/sentinelx/assets@main/logo.png",
          alt_text: "SentinelX",
        },
      },
      {
        type: "section",
        fields: [
          { type: "mrkdwn", text: `*Total Events:*\n${report.totalEvents.toLocaleString()}`, verbatim: false },
          { type: "mrkdwn", text: `*Threats Blocked:*\n${report.threatsBlocked}`, verbatim: false },
          { type: "mrkdwn", text: `*Threats Rewritten:*\n${report.threatsRewritten}`, verbatim: false },
          { type: "mrkdwn", text: `*Allowed:*\n${report.totalEvents - report.threatsBlocked - report.threatsRewritten}`, verbatim: false },
        ],
      },
      {
        type: "actions",
        elements: [
          {
            type: "button",
            text: { type: "plain_text", text: "View Full Report" },
            style: "primary",
            url: `${process.env.NEXT_PUBLIC_APP_URL}/compliance`,
          },
        ],
      },
    ],
  }
}