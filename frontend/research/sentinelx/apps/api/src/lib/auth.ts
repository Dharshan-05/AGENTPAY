import jwt from "jsonwebtoken"
import type { FastifyRequest, FastifyReply } from "fastify"

const JWT_SECRET = process.env.JWT_SECRET || "sentinelx-dev-jwt-secret-change-in-production"
const JWT_EXPIRES_IN = "24h"

export interface TokenPayload {
  sub: string
  email: string
  name: string
  picture?: string
  role: string
}

export function signToken(payload: TokenPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN })
}

export function verifyToken(token: string): TokenPayload | null {
  try {
    return jwt.verify(token, JWT_SECRET) as TokenPayload
  } catch {
    return null
  }
}

export async function verifyGoogleToken(accessToken: string): Promise<{ email: string; name: string; picture?: string; emailVerified?: boolean } | null> {
  try {
    const res = await fetch(`https://www.googleapis.com/oauth2/v3/userinfo`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
    if (!res.ok) return null
    const data = await res.json() as { email: string; name: string; picture?: string; email_verified?: boolean }
    if (!data.email) return null
    return { email: data.email, name: data.name, picture: data.picture, emailVerified: data.email_verified ?? false }
  } catch {
    return null
  }
}

export function getAuthCookie(token: string): { name: string; value: string; options: Record<string, unknown> } {
  return {
    name: "sentinelx_token",
    value: token,
    options: {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 60 * 60 * 24,
    },
  }
}

// Extract token from Authorization header or cookie
export function extractToken(request: FastifyRequest): string | null {
  const authHeader = request.headers.authorization
  if (authHeader?.startsWith("Bearer ")) {
    return authHeader.slice(7)
  }
  // Check cookie
  const cookies = (request as any).cookies as Record<string, string> | undefined
  return cookies?.["sentinelx_token"] ?? null
}

// Fastify middleware for JWT authentication
export async function authMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<TokenPayload | null> {
  const token = extractToken(request)
  if (!token) {
    return reply.code(401).send({ error: "Authentication required" })
  }
  const payload = verifyToken(token)
  if (!payload) {
    return reply.code(401).send({ error: "Invalid or expired token" })
  }
  // Attach user to request for downstream use
  ;(request as any).user = payload
  return payload
}

export interface GatewayAuthPayload {
  apiKeyId: string
  userId: string
  organizationId: string | null
  scopes: any
}

// Fastify middleware for API Key authentication
export async function apiKeyAuthMiddleware(request: FastifyRequest, reply: FastifyReply) {
  const authHeader = request.headers.authorization
  if (!authHeader?.startsWith("Bearer sx_live_")) {
    return reply.code(401).send({ error: "Unauthorized" })
  }
  
  const rawSecret = authHeader.slice(7)
  const { hashIncomingKey } = await import("./api-keys")
  const { store } = await import("./store")

  const keyHash = hashIncomingKey(rawSecret)
  
  const apiKey = await store.apiKey.findFirst({
    where: { keyHash }
  })

  if (!apiKey) {
    return reply.code(401).send({ error: "Unauthorized" })
  }

  if (apiKey.status !== "ACTIVE") {
    return reply.code(401).send({ error: "Unauthorized" })
  }

  if (apiKey.expiresAt && apiKey.expiresAt < new Date()) {
    return reply.code(401).send({ error: "Unauthorized" })
  }

  if (apiKey.revokedAt && apiKey.revokedAt <= new Date()) {
    return reply.code(401).send({ error: "Unauthorized" })
  }

  // Check if associated user exists and is active (optional, depending on user model)
  const user = await store.user.findUnique({ where: { id: apiKey.userId as string } })
  if (!user) {
    return reply.code(401).send({ error: "Unauthorized" })
  }

  // Defer updating lastUsedAt to avoid blocking
  store.apiKey.update({
    where: { id: apiKey.id },
    data: { lastUsedAt: new Date() }
  }).catch(() => {})

  const payload: GatewayAuthPayload = {
    apiKeyId: apiKey.id as string,
    userId: apiKey.userId as string,
    organizationId: (apiKey.organizationId as string | null) || null,
    scopes: apiKey.scopes as string[] | null
  }

  ;(request as any).gatewayAuth = payload
}