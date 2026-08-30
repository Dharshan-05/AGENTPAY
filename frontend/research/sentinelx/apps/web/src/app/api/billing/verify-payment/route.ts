import { NextRequest, NextResponse } from "next/server"
import crypto from "crypto"

const RAZORPAY_KEY_SECRET = process.env.RAZORPAY_KEY_SECRET ?? ""

export async function POST(request: NextRequest) {
  try {
    const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = await request.json()

    if (!razorpay_order_id || !razorpay_payment_id || !razorpay_signature) {
      return NextResponse.json(
        { error: "Missing payment verification data" },
        { status: 400 }
      )
    }

    if (!RAZORPAY_KEY_SECRET) {
      // Demo mode - accept all
      return NextResponse.json({ success: true })
    }

    const body = `${razorpay_order_id}|${razorpay_payment_id}`
    const expectedSignature = crypto
      .createHmac("sha256", RAZORPAY_KEY_SECRET)
      .update(body)
      .digest("hex")

    if (expectedSignature !== razorpay_signature) {
      return NextResponse.json(
        { error: "Invalid payment signature" },
        { status: 400 }
      )
    }

    // Payment verified successfully
    // In a real app, you would update the user's subscription status here
    // and store the payment record in the database

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("Payment verification error:", error)
    return NextResponse.json(
      { error: "Payment verification failed" },
      { status: 500 }
    )
  }
}