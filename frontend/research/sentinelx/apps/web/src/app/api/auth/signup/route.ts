import { NextRequest, NextResponse } from "next/server"
import { createUser, getUser } from "@/lib/auth-config"

export async function POST(request: NextRequest) {
  try {
    const { name, email, password } = await request.json()
    
    if (!name || !email || !password) {
      return NextResponse.json(
        { error: "Name, email, and password are required" },
        { status: 400 }
      )
    }
    
    if (password.length < 8) {
      return NextResponse.json(
        { error: "Password must be at least 8 characters" },
        { status: 400 }
      )
    }
    
    const existingUser = await getUser(email.toLowerCase())
    if (existingUser) {
      return NextResponse.json(
        { error: "Email already registered" },
        { status: 409 }
      )
    }
    
    const user = await createUser(email, password, name, "employee")
    
    return NextResponse.json({
      success: true,
      user: {
        id: `user-${email.replace(/[^a-z0-9]/gi, "")}`,
        email: user.email,
        name: user.name,
        role: user.role,
      },
    })
  } catch (error) {
    console.error("Signup error:", error)
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}