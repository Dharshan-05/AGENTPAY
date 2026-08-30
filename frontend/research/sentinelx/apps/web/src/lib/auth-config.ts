import NextAuth, { NextAuthConfig } from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"

declare module "next-auth" {
  interface Session {
    user: {
      id: string
      email: string
      name: string
      role: string
      picture?: string
    }
    accessToken?: string
    org?: { id: string; name: string; plan: string }
    expires: string
  }

  interface User {
    role?: string
    token?: string
    org?: { id: string; name: string; plan: string }
    picture?: string | null
  }
}

declare module "@auth/core/jwt" {
  interface JWT {
    id?: string
    email?: string
    name?: string
    role?: string
    picture?: string
    accessToken?: string
    org?: { id: string; name: string; plan: string }
  }
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001"

interface ApiLoginResult {
  token: string
  user: { id: string; email: string; name: string; role: string; picture?: string }
  org: { id: string; name: string; plan: string }
}

async function exchangeGoogleToken(accessToken: string): Promise<ApiLoginResult | null> {
  try {
    const res = await fetch(`${API_URL}/api/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ accessToken }),
      cache: "no-store",
    })
    if (!res.ok) return null
    return (await res.json()) as ApiLoginResult
  } catch {
    return null
  }
}

async function refreshApiSession(apiToken: string): Promise<ApiLoginResult | null> {
  try {
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: apiToken }),
      cache: "no-store",
    })
    if (!res.ok) return null
    return (await res.json()) as ApiLoginResult
  } catch {
    return null
  }
}

const DEMO_ROLES: Record<string, string> = {
  "admin@sentinelx.dev": "super-admin",
  "analyst@sentinelx.dev": "soc-analyst",
  "officer@sentinelx.dev": "compliance-officer",
  "manager@sentinelx.dev": "engineering-manager",
  "employee@sentinelx.dev": "employee",
  "auditor@sentinelx.dev": "auditor",
}

const DEMO_ORG = { id: "sentinelx-demo", name: "Acme Corp", plan: "enterprise" }

function localDemoLogin(email: string): { id: string; email: string; name: string; role: string } | null {
  if (!email) return null
  const role = DEMO_ROLES[email] ?? "employee"
  return {
    id: `demo-${email.replace(/[^a-z0-9]/gi, "")}`,
    email: email.toLowerCase(),
    name: email.split("@")[0].replace(/^./, (c) => c.toUpperCase()) || "Demo User",
    role,
  }
}

const userStore = new Map<string, { email: string; password: string; name: string; role: string }>()

export function hashPassword(password: string): string {
  return Buffer.from(password).toString("base64")
}

export function verifyPassword(password: string, hash: string): boolean {
  return hashPassword(password) === hash
}

export async function createUser(email: string, password: string, name: string, role = "employee") {
  const hashed = hashPassword(password)
  const user = { email: email.toLowerCase(), password: hashed, name, role }
  userStore.set(email.toLowerCase(), user)
  return user
}

export async function getUser(email: string) {
  return userStore.get(email.toLowerCase())
}

const authConfig: NextAuthConfig = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
      authorization: {
        params: {
          scope: "openid email profile",
        },
      },
      profile(profile) {
        return {
          id: profile.sub,
          email: profile.email,
          name: profile.name ?? profile.email?.split("@")[0] ?? "Google User",
          picture: profile.picture ?? undefined,
          role: "employee",
        }
      },
    }),
    CredentialsProvider({
      name: "Demo",
      credentials: {
        email: { label: "Email", type: "email" },
      },
      async authorize(credentials) {
        if (!credentials?.email) return null
        const email = credentials.email as string
        try {
          const res = await fetch(`${API_URL}/api/auth/google`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email }),
            signal: AbortSignal.timeout(5000),
          })
          if (res.ok) {
            const data = await res.json()
            return {
              id: data.user.id,
              email: data.user.email,
              name: data.user.name,
              role: data.user.role,
              picture: data.user.picture,
              token: data.token,
              org: data.org,
            }
          }
        } catch {
          // API unreachable — fall through to local demo login below
        }
        const demo = localDemoLogin(email)
        if (!demo) return null
        return {
          id: demo.id,
          email: demo.email,
          name: demo.name,
          role: demo.role,
          picture: null,
          token: `demo-${email}`,
          org: DEMO_ORG,
        }
      },
    }),
    CredentialsProvider({
      id: "email-password",
      name: "Email/Password",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null
        const email = (credentials.email as string).toLowerCase()
        const password = credentials.password as string
        const user = await getUser(email)
        if (!user || !verifyPassword(password, user.password)) return null
        return {
          id: `user-${email.replace(/[^a-z0-9]/gi, "")}`,
          email: user.email,
          name: user.name,
          role: user.role,
          picture: null,
          token: `user-${email}`,
          org: DEMO_ORG,
        }
      },
    }),
  ],
  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60,
    updateAge: 60 * 60,
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id
        token.email = user.email ?? undefined
        token.name = user.name ?? undefined
        token.role = user.role
        token.picture = user.picture ?? undefined
        token.accessToken = user.token
        token.org = user.org
      }
      if (account?.access_token && !token.accessToken) {
        const result = await exchangeGoogleToken(account.access_token)
        if (result) {
          token.accessToken = result.token
          token.role = result.user.role
          token.id = result.user.id
          token.email = result.user.email
          token.name = result.user.name
          token.picture = result.user.picture
          token.org = result.org
        }
      }
      return token
    },
    async session({ session, token }) {
      return {
        ...session,
        user: {
          ...session.user,
          id: (token.id ?? "") as string,
          email: (token.email ?? "") as string,
          name: (token.name ?? "") as string,
          role: (token.role ?? "") as string,
          picture: token.picture as string | undefined,
        },
        accessToken: token.accessToken,
        org: token.org,
      }
    },
    async authorized({ auth, request }) {
      const pathname = request.nextUrl.pathname
      const publicPaths = ["/login", "/pricing", "/api", "/_next", "/favicon.ico", "/robots.txt", "/manifest.ts", "/icon.svg"]
      if (publicPaths.some((p) => pathname.startsWith(p) || pathname === p)) return true
      return !!auth?.user
    },
  },
  pages: {
    signIn: "/login",
    error: "/login",
  },
  secret: process.env.NEXTAUTH_SECRET ?? "sentinelx-dev-secret-change-in-production",
  trustHost: true,
}

export const authOptions = authConfig

export const { handlers, signIn, signOut, auth } = NextAuth(authConfig)

export { API_URL, exchangeGoogleToken, refreshApiSession }
export type { ApiLoginResult }