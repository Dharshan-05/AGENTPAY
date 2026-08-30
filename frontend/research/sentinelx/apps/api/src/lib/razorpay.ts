import Razorpay from "razorpay"
import crypto from "crypto"

const RAZORPAY_KEY_ID = process.env.RAZORPAY_KEY_ID
const RAZORPAY_KEY_SECRET = process.env.RAZORPAY_KEY_SECRET

let razorpay: Razorpay | null = null
let configured = false

if (RAZORPAY_KEY_ID && RAZORPAY_KEY_SECRET) {
  razorpay = new Razorpay({
    key_id: RAZORPAY_KEY_ID,
    key_secret: RAZORPAY_KEY_SECRET,
  })
  configured = true
  console.log("[Razorpay] Configured")
} else {
  console.log("[Razorpay] Not configured — running in demo mode")
}

export interface RazorpayOrder {
  id: string
  entity: string
  amount: number
  amount_paid: number
  amount_due: number
  currency: string
  receipt: string
  offer_id: string | null
  status: string
  attempts: number
  notes: Record<string, string>
  created_at: number
}

export interface RazorpaySubscription {
  id: string
  entity: string
  plan_id: string
  customer_id: string
  status: string
  current_start: number
  current_end: number
  ended_at: number | null
  quantity: number
  notes: Record<string, string>
  charge_at: number
  start_at: number
  end_at: number
  auth_attempts: number
  total_count: number
  paid_count: number
  customer_notify: boolean
  created_at: number
  expire_by: number | null
  remaining_count: number
}

export interface RazorpayCustomer {
  id: string
  entity: string
  name: string
  email: string
  contact: string
  gstin: string | null
  notes: Record<string, string>
  created_at: number
}

export interface RazorpayInvoice {
  id: string
  entity: string
  amount: number
  amount_paid: number
  amount_due: number
  currency: string
  status: string
  receipt: string
  description: string
  customer_id: string
  date: number
  due_date: number
  paid_at: number | null
  notes: Record<string, string>
  line_items: Array<{
    name: string
    description: string
    amount: number
    currency: string
    quantity: number
  }>
}

export function isRazorpayConfigured(): boolean {
  return configured
}

export function getRazorpayClient(): Razorpay | null {
  return razorpay
}

export async function createOrder(params: {
  amount: number
  currency: string
  receipt: string
  notes?: Record<string, string>
}): Promise<RazorpayOrder | null> {
  if (!razorpay) {
    // Demo mode - return mock order
    return {
      id: `order_demo_${Date.now()}`,
      entity: "order",
      amount: params.amount,
      amount_paid: 0,
      amount_due: params.amount,
      currency: params.currency,
      receipt: params.receipt,
      offer_id: null,
      status: "created",
      attempts: 0,
      notes: params.notes ?? {},
      created_at: Math.floor(Date.now() / 1000),
    }
  }

  try {
    const order = await razorpay.orders.create({
      amount: params.amount,
      currency: params.currency,
      receipt: params.receipt,
      notes: params.notes,
    })
    return order as RazorpayOrder
  } catch (error) {
    console.error("[Razorpay] Create order failed:", error)
    return null
  }
}

export async function createSubscription(params: {
  plan_id: string
  customer_id: string
  total_count?: number
  quantity?: number
  customer_notify?: boolean
  notes?: Record<string, string>
}): Promise<RazorpaySubscription | null> {
  if (!razorpay) {
    return {
      id: `sub_demo_${Date.now()}`,
      entity: "subscription",
      plan_id: params.plan_id,
      customer_id: params.customer_id,
      status: "created",
      current_start: Math.floor(Date.now() / 1000),
      current_end: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60,
      ended_at: null,
      quantity: params.quantity ?? 1,
      notes: params.notes ?? {},
      charge_at: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60,
      start_at: Math.floor(Date.now() / 1000),
      end_at: Math.floor(Date.now() / 1000) + 365 * 24 * 60 * 60,
      auth_attempts: 0,
      total_count: params.total_count ?? 12,
      paid_count: 0,
      customer_notify: params.customer_notify ?? true,
      created_at: Math.floor(Date.now() / 1000),
      expire_by: null,
      remaining_count: params.total_count ?? 12,
    } as RazorpaySubscription
  }

  try {
    const subscription = await razorpay.subscriptions.create({
      plan_id: params.plan_id,
      total_count: params.total_count ?? 12,
      quantity: params.quantity ?? 1,
      customer_notify: params.customer_notify ?? true,
      notes: params.notes,
    })
    return subscription as unknown as RazorpaySubscription
  } catch (error) {
    console.error("[Razorpay] Create subscription failed:", error)
    return null
  }
}

export async function createCustomer(params: {
  name: string
  email: string
  contact: string
  gstin?: string
  notes?: Record<string, string>
}): Promise<RazorpayCustomer | null> {
  if (!razorpay) {
    return {
      id: `cust_demo_${Date.now()}`,
      entity: "customer",
      name: params.name,
      email: params.email,
      contact: params.contact,
      gstin: params.gstin ?? null,
      notes: params.notes ?? {},
      created_at: Math.floor(Date.now() / 1000),
    }
  }

  try {
    const customer = await razorpay.customers.create({
      name: params.name,
      email: params.email,
      contact: params.contact,
      gstin: params.gstin,
      notes: params.notes,
    })
    return customer as RazorpayCustomer
  } catch (error) {
    console.error("[Razorpay] Create customer failed:", error)
    return null
  }
}

export async function fetchSubscription(subscriptionId: string): Promise<RazorpaySubscription | null> {
  if (!razorpay) {
    return {
      id: subscriptionId,
      entity: "subscription",
      plan_id: "plan_enterprise",
      customer_id: "cust_demo_123",
      status: "active",
      current_start: Math.floor(Date.now() / 1000),
      current_end: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60,
      ended_at: null,
      quantity: 1,
      notes: {},
      charge_at: Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60,
      start_at: Math.floor(Date.now() / 1000) - 30 * 24 * 60 * 60,
      end_at: Math.floor(Date.now() / 1000) + 335 * 24 * 60 * 60,
      auth_attempts: 0,
      total_count: 12,
      paid_count: 1,
      customer_notify: true,
      created_at: Math.floor(Date.now() / 1000) - 30 * 24 * 60 * 60,
      expire_by: null,
      remaining_count: 11,
    } as RazorpaySubscription
  }

  try {
    return (await razorpay.subscriptions.fetch(subscriptionId)) as unknown as RazorpaySubscription
  } catch (error) {
    console.error("[Razorpay] Fetch subscription failed:", error)
    return null
  }
}

export async function cancelSubscription(subscriptionId: string): Promise<boolean> {
  if (!razorpay) return true

  try {
    await razorpay.subscriptions.cancel(subscriptionId)
    return true
  } catch (error) {
    console.error("[Razorpay] Cancel subscription failed:", error)
    return false
  }
}

export async function fetchInvoices(customerId: string): Promise<RazorpayInvoice[]> {
  if (!razorpay) {
    return [
      {
        id: "inv_demo_1",
        entity: "invoice",
        amount: 499900,
        amount_paid: 499900,
        amount_due: 0,
        currency: "INR",
        status: "paid",
        receipt: "rcpt_demo_1",
        description: "SentinelX Enterprise - Monthly",
        customer_id: customerId,
        date: Math.floor(Date.now() / 1000) - 30 * 24 * 60 * 60,
        due_date: Math.floor(Date.now() / 1000) - 30 * 24 * 60 * 60,
        paid_at: Math.floor(Date.now() / 1000) - 30 * 24 * 60 * 60 + 3600,
        notes: {},
        line_items: [
          { name: "Enterprise Plan", description: "Monthly subscription", amount: 499900, currency: "INR", quantity: 1 },
        ],
      },
      {
        id: "inv_demo_2",
        entity: "invoice",
        amount: 499900,
        amount_paid: 499900,
        amount_due: 0,
        currency: "INR",
        status: "paid",
        receipt: "rcpt_demo_2",
        description: "SentinelX Enterprise - Monthly",
        customer_id: customerId,
        date: Math.floor(Date.now() / 1000) - 60 * 24 * 60 * 60,
        due_date: Math.floor(Date.now() / 1000) - 60 * 24 * 60 * 60,
        paid_at: Math.floor(Date.now() / 1000) - 60 * 24 * 60 * 60 + 3600,
        notes: {},
        line_items: [
          { name: "Enterprise Plan", description: "Monthly subscription", amount: 499900, currency: "INR", quantity: 1 },
        ],
      },
    ]
  }

  try {
    const invoices = await razorpay.invoices.all({ customer_id: customerId })
    return invoices.items as unknown as RazorpayInvoice[]
  } catch (error) {
    console.error("[Razorpay] Fetch invoices failed:", error)
    return []
  }
}

export async function fetchInvoice(invoiceId: string): Promise<RazorpayInvoice | null> {
  if (!razorpay) return null

  try {
    return (await razorpay.invoices.fetch(invoiceId)) as unknown as RazorpayInvoice
  } catch (error) {
    console.error("[Razorpay] Fetch invoice failed:", error)
    return null
  }
}

export function verifyWebhookSignature(
  body: string,
  signature: string,
  secret: string
): boolean {
  if (!configured) return true // Demo mode - accept all

  try {
    const expectedSignature = crypto
      .createHmac("sha256", secret)
      .update(body)
      .digest("hex")
    return expectedSignature === signature
  } catch {
    return false
  }
}

export function healthCheck(): { configured: boolean; keyId?: string } {
  if (!configured) return { configured: false }
  return { configured, keyId: RAZORPAY_KEY_ID?.slice(0, 8) + "..." }
}

export const PLANS = {
  trial: {
    id: "plan_trial",
    name: "Trial",
    price: 900, // INR 9 (in paise)
    currency: "INR",
    interval: "one_time",
    features: {
      users: 5,
      aiRequests: 1000,
      storage: 1, // GB
      compliancePacks: 1,
      prioritySupport: false,
      socDashboard: false,
      unlimitedAuditLogs: false,
      enterpriseSSO: false,
      apiAccess: true,
      customPolicies: false,
    },
  },
  starter: {
    id: "plan_starter",
    name: "Starter",
    price: 4900, // INR 49/month (in paise)
    currency: "INR",
    interval: "monthly",
    features: {
      users: 5,
      aiRequests: 10000,
      storage: 10, // GB
      compliancePacks: 2,
      prioritySupport: false,
      socDashboard: false,
      unlimitedAuditLogs: false,
      enterpriseSSO: false,
      apiAccess: true,
      customPolicies: false,
    },
  },
  professional: {
    id: "plan_professional",
    name: "Professional",
    price: 14900, // INR 149/month (in paise)
    currency: "INR",
    interval: "monthly",
    features: {
      users: 25,
      aiRequests: 100000,
      storage: 100, // GB
      compliancePacks: 5,
      prioritySupport: true,
      socDashboard: true,
      unlimitedAuditLogs: true,
      enterpriseSSO: false,
      apiAccess: true,
      customPolicies: true,
    },
  },
  enterprise: {
    id: "plan_enterprise",
    name: "Enterprise",
    price: 49900, // INR 499/month (in paise)
    currency: "INR",
    interval: "monthly",
    features: {
      users: -1, // unlimited
      aiRequests: -1, // unlimited
      storage: -1, // unlimited
      compliancePacks: 5,
      prioritySupport: true,
      socDashboard: true,
      unlimitedAuditLogs: true,
      enterpriseSSO: true,
      apiAccess: true,
      customPolicies: true,
    },
  },
} as const