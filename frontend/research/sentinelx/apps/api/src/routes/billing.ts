import type { FastifyInstance } from "fastify"
import {
  createOrder,
  createSubscription,
  createCustomer,
  fetchSubscription,
  cancelSubscription,
  fetchInvoices,
  fetchInvoice,
  verifyWebhookSignature,
  healthCheck,
  PLANS,
} from "../lib/razorpay"
import { authMiddleware } from "../lib/auth"

export async function registerBillingRoutes(app: FastifyInstance): Promise<void> {
  app.get("/api/billing/health", { preHandler: authMiddleware }, async () => {
    return healthCheck()
  })

  app.get("/api/billing/plans", { preHandler: authMiddleware }, async () => {
    return PLANS
  })

  app.post("/api/billing/create-order", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      planId: keyof typeof PLANS
      billingCycle: "monthly" | "yearly" | "one_time"
    }

    const plan = PLANS[body.planId]
    if (!plan) {
      return reply.code(400).send({ error: "Invalid plan" })
    }

    let amount: number
    switch (body.billingCycle) {
      case "yearly":
        amount = Math.round(plan.price * 10) // ~10 months = 2 months free
        break
      case "one_time":
        amount = plan.price
        break
      case "monthly":
      default:
        amount = plan.price
        break
    }

    const order = await createOrder({
      amount,
      currency: plan.currency,
      receipt: `rcpt_${(request as any).user?.sub}_${Date.now()}`,
      notes: {
        planId: body.planId,
        billingCycle: body.billingCycle,
        userId: (request as any).user?.sub ?? "",
      },
    })

    if (!order) {
      return reply.code(500).send({ error: "Failed to create order" })
    }

    return { order, plan, amount }
  })

  app.post("/api/billing/create-subscription", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      planId: keyof typeof PLANS
      customerId?: string
    }

    const plan = PLANS[body.planId]
    if (!plan) {
      return reply.code(400).send({ error: "Invalid plan" })
    }

    const userId = (request as any).user?.sub
    let customerId = body.customerId

    // Create customer if needed
    if (!customerId) {
      const customer = await createCustomer({
        name: (request as any).user?.name ?? "SentinelX User",
        email: (request as any).user?.email ?? "user@sentinelx.dev",
        contact: "+91-9999999999",
        notes: { userId: userId ?? "" },
      })
      customerId = customer?.id
    }

    if (!customerId) {
      return reply.code(500).send({ error: "Failed to create customer" })
    }

    const subscription = await createSubscription({
      plan_id: plan.id,
      customer_id: customerId,
      notes: { userId: userId ?? "" },
    })

    if (!subscription) {
      return reply.code(500).send({ error: "Failed to create subscription" })
    }

    return { subscription, customerId }
  })

  app.get("/api/billing/subscription/:subscriptionId", { preHandler: authMiddleware }, async (request, reply) => {
    const { subscriptionId } = request.params as { subscriptionId: string }
    const subscription = await fetchSubscription(subscriptionId)

    if (!subscription) {
      return reply.code(404).send({ error: "Subscription not found" })
    }

    return subscription
  })

  app.post("/api/billing/cancel-subscription/:subscriptionId", { preHandler: authMiddleware }, async (request, reply) => {
    const { subscriptionId } = request.params as { subscriptionId: string }
    const success = await cancelSubscription(subscriptionId)

    if (!success) {
      return reply.code(500).send({ error: "Failed to cancel subscription" })
    }

    return { success: true }
  })

  app.get("/api/billing/invoices", { preHandler: authMiddleware }, async (request) => {
    const user = (request as any).user
    const customerId = `cust_demo_${user?.sub ?? "123"}`
    const invoices = await fetchInvoices(customerId)
    return { invoices }
  })

  app.get("/api/billing/invoice/:invoiceId", { preHandler: authMiddleware }, async (request, reply) => {
    const { invoiceId } = request.params as { invoiceId: string }
    const invoice = await fetchInvoice(invoiceId)

    if (!invoice) {
      return reply.code(404).send({ error: "Invoice not found" })
    }

    return invoice
  })

  app.post("/api/billing/webhook", async (request, reply) => {
    const signature = request.headers["x-razorpay-signature"] as string
    const body = JSON.stringify(request.body)

    const secret = process.env.RAZORPAY_WEBHOOK_SECRET ?? ""
    if (secret && !verifyWebhookSignature(body, signature, secret)) {
      return reply.code(400).send({ error: "Invalid signature" })
    }

    const event = request.body as { event: string; payload: any }
    console.log("[Razorpay Webhook] Received:", event.event)

    // Handle events: payment.captured, subscription.activated, subscription.charged, etc.
    switch (event.event) {
      case "payment.captured":
        // Payment successful - update subscription status
        console.log("[Razorpay] Payment captured:", event.payload.payment.entity.id)
        break
      case "subscription.activated":
        console.log("[Razorpay] Subscription activated:", event.payload.subscription.entity.id)
        break
      case "subscription.charged":
        console.log("[Razorpay] Subscription charged:", event.payload.subscription.entity.id)
        break
      case "subscription.cancelled":
        console.log("[Razorpay] Subscription cancelled:", event.payload.subscription.entity.id)
        break
      case "invoice.paid":
        console.log("[Razorpay] Invoice paid:", event.payload.invoice.entity.id)
        break
      case "invoice.payment_failed":
        console.log("[Razorpay] Invoice payment failed:", event.payload.invoice.entity.id)
        break
    }

    return { received: true }
  })

  // Current user's subscription (no ID required)
  app.get("/api/billing/subscription", { preHandler: authMiddleware }, async (request) => {
    const user = (request as any).user
    const userId = user?.sub ?? "demo"
    // Return a demo active subscription — replace with real DB lookup when Razorpay subs are stored
    return {
      subscription: {
        id: `sub_demo_${userId}`,
        plan_id: "plan_enterprise",
        status: "active",
        current_period_start: Math.floor(Date.now() / 1000) - 86400 * 15,
        current_period_end: Math.floor(Date.now() / 1000) + 86400 * 15,
        quantity: 1,
      },
    }
  })

  app.get("/api/billing/usage", { preHandler: authMiddleware }, async () => {
    // Demo usage data
    return {
      current: {
        protectedPrompts: 1247,
        llmCalls: 3892,
        storageUsed: 2.4, // GB
        incidents: 23,
        reportsGenerated: 12,
        complianceChecks: 456,
      },
      limits: {
        protectedPrompts: -1,
        llmCalls: -1,
        storage: -1,
        incidents: -1,
        reportsGenerated: -1,
        complianceChecks: -1,
      },
      history: [
        { month: "Jan", protectedPrompts: 980, llmCalls: 2100, storage: 1.8, incidents: 15, reports: 8, checks: 320 },
        { month: "Feb", protectedPrompts: 1100, llmCalls: 2800, storage: 2.1, incidents: 18, reports: 10, checks: 380 },
        { month: "Mar", protectedPrompts: 1247, llmCalls: 3892, storage: 2.4, incidents: 23, reports: 12, checks: 456 },
      ],
      forecast: {
        nextMonth: { protectedPrompts: 1450, llmCalls: 4200, storage: 2.8, incidents: 28, reports: 15, checks: 520 },
      },
    }
  })

  app.get("/api/billing/analytics", { preHandler: authMiddleware }, async () => {
    // Demo billing analytics
    return {
      mrr: 499900,
      arr: 5998800,
      activeSubscriptions: 1,
      trialUsers: 0,
      enterpriseCustomers: 1,
      paymentSuccessRate: 100,
      refundRate: 0,
      monthlyGrowth: 12.5,
      revenueHistory: [
        { month: "Jan", revenue: 499900, subscriptions: 1 },
        { month: "Feb", revenue: 499900, subscriptions: 1 },
        { month: "Mar", revenue: 499900, subscriptions: 1 },
      ],
    }
  })
}