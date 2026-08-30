import { NextRequest, NextResponse } from "next/server"
import { healthCheck, captureError, captureMessage, addBreadcrumb } from "@/lib/sentry"
import { auth } from "@/lib/auth-config"

export async function GET() {
  return NextResponse.json(healthCheck())
}

export async function POST(request: NextRequest) {
  try {
    const session = await auth()
    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    const body = await request.json()
    const { type } = body

    switch (type) {
      case "test-error":
        try {
          throw new Error("Test error from SentinelX Web")
        } catch (error) {
          const eventId = captureError(error as Error, { test: true, userId: (session.user as any).id })
          return NextResponse.json({ eventId, message: "Test error captured" })
        }

      case "test-message":
        const eventId = captureMessage("Test message from SentinelX Web", "info", { test: true })
        return NextResponse.json({ eventId, message: "Test message captured" })

      case "breadcrumb":
        addBreadcrumb({
          category: body.category,
          message: body.message,
          level: body.level || "info",
          data: body.data,
          timestamp: Date.now() / 1000,
        })
        return NextResponse.json({ success: true })

      default:
        return NextResponse.json({ error: "Unknown type" }, { status: 400 })
    }
  } catch (error) {
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 })
  }
}