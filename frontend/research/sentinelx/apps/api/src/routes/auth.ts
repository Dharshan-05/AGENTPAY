import type { FastifyInstance } from "fastify"
import { signToken, verifyToken, verifyGoogleToken, getAuthCookie } from "../lib/auth"
import { store } from "../lib/store"

const ROOT_ORG = {
  id: "sentinelx-demo",
  name: "Acme Corp",
  plan: "enterprise",
}

const DEMO_USERS: Record<string, { name: string; role: string; picture?: string }> = {
  "admin@sentinelx.dev": { name: "Aarav Mehta", role: "super-admin", picture: undefined },
  "analyst@sentinelx.dev": { name: "Kenji Watanabe", role: "soc-analyst", picture: undefined },
  "officer@sentinelx.dev": { name: "Sofia Reyes", role: "compliance-officer", picture: undefined },
  "manager@sentinelx.dev": { name: "Daniel Okafor", role: "engineering-manager", picture: undefined },
  "employee@sentinelx.dev": { name: "Meera Kapoor", role: "employee", picture: undefined },
  "auditor@sentinelx.dev": { name: "Maya Iyer", role: "auditor", picture: undefined },
}

function publicUser(user: Record<string, unknown>): Record<string, unknown> {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role,
    picture: user.avatarUrl ?? user.picture ?? null,
    provider: user.provider ?? "unknown",
    emailVerified: user.emailVerified ?? false,
    lastLoginAt: user.lastLoginAt ?? null,
  }
}

function signUserToken(user: Record<string, unknown>, fallbackPicture?: string): string {
  return signToken({
    sub: user.id as string,
    email: user.email as string,
    name: user.name as string,
    picture: (user.avatarUrl as string) ?? fallbackPicture,
    role: user.role as string,
  })
}

export async function registerAuthRoutes(app: FastifyInstance) {
  app.post("/api/auth/google", async (request, reply) => {
    const body = request.body as { accessToken?: string; email?: string }

    let email: string
    let name: string
    let picture: string | undefined
    let provider = "google"
    let emailVerified = false

    if (body.accessToken) {
      const user = await verifyGoogleToken(body.accessToken)
      if (!user) {
        return reply.code(401).send({ error: "Invalid Google token" })
      }
      email = user.email
      name = user.name
      picture = user.picture
      provider = "google"
      emailVerified = user.emailVerified ?? false
    } else if (body.email && (process.env.NODE_ENV !== "production" || process.env.DEMO_MODE === "true" || DEMO_USERS[body.email])) {
      email = body.email
      const demo = DEMO_USERS[email]
      name = demo?.name ?? email.split("@")[0]
      picture = demo?.picture
      provider = "demo"
      emailVerified = true
    } else {
      return reply.code(400).send({ error: "accessToken or demo email required" })
    }

    let user = await store.user.findFirst({ where: { email } }) as Record<string, unknown> | null
    if (!user) {
      const role = DEMO_USERS[email]?.role ?? ((await store.user.count()) === 0 ? "super-admin" : "employee")
      const created = await store.user.create({
        data: {
          email,
          name,
          role,
          avatarUrl: picture ?? null,
          department: role === "employee" ? "Engineering" : "Security",
          provider,
          emailVerified,
          lastLoginAt: new Date().toISOString(),
        },
      })
      user = created as Record<string, unknown>
    } else {
      await store.user.update({
        where: { id: user.id as string },
        data: {
          provider,
          emailVerified,
          lastLoginAt: new Date().toISOString(),
        },
      })
      user = { ...user, provider, emailVerified, lastLoginAt: new Date().toISOString() }
    }

    const token = signUserToken(user, picture ?? undefined)

    const cookie = getAuthCookie(token)
    reply.header("Set-Cookie", `${cookie.name}=${cookie.value}; HttpOnly; ${cookie.options.secure ? 'Secure;' : ''} SameSite=${cookie.options.sameSite}; Path=${cookie.options.path}; Max-Age=${cookie.options.maxAge}`)

    return reply.send({
      token,
      user: publicUser(user),
      org: ROOT_ORG,
    })
  })

  app.post("/api/auth/refresh", async (request, reply) => {
    const body = request.body as { token?: string }
    const header = request.headers.authorization
    const raw = body.token ?? (header?.startsWith("Bearer ") ? header.slice(7) : null)
    if (!raw) {
      return reply.code(401).send({ error: "No token" })
    }
    const payload = verifyToken(raw)
    if (!payload) {
      return reply.code(401).send({ error: "Invalid or expired token" })
    }
    try {
      const user = await store.user.findUnique({ where: { id: payload.sub } }) 
      if (!user) {
        return reply.code(404).send({ error: "User not found" })
      }
      const token = signUserToken(user, payload.picture ?? undefined)
      return reply.send({
        token,
        user: publicUser(user),
        org: ROOT_ORG,
      })
    } catch {
      return reply.code(401).send({ error: "Session could not be refreshed" })
    }
  })

  app.get("/api/auth/me", async (request, reply) => {
    const header = request.headers.authorization
    if (!header?.startsWith("Bearer ")) {
      return reply.code(401).send({ error: "No token" })
    }
    const payload = verifyToken(header.slice(7))
    if (!payload) {
      return reply.code(401).send({ error: "Invalid token" })
    }

    try {
      const user = await store.user.findUnique({ where: { id: payload.sub } })
      if (!user) {
        return reply.code(404).send({ error: "User not found" })
      }
      return reply.send({
        ...publicUser(user),
        org: ROOT_ORG,
      })
    } catch {
      return reply.send({
        id: payload.sub,
        email: payload.email,
        name: payload.name,
        role: payload.role,
        picture: payload.picture,
        provider: "google",
        emailVerified: true,
        lastLoginAt: null,
        org: ROOT_ORG,
      })
    }
  })

  app.post("/api/auth/logout", async (_request, reply) => {
    reply.header("Set-Cookie", "sentinelx_token=; max-Age=0; Path=/")
    return reply.send({ ok: true })
  })
}