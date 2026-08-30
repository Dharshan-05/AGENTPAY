"use client"

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"
import { SessionProvider, useSession, signIn, signOut } from "next-auth/react"
import type { RoleId } from "@/lib/rbac"
import { ROLES } from "@/lib/rbac"
import { setAuthToken } from "@/lib/auth-token"

export interface User {
  id: string
  email: string
  name: string
  role: string
  picture?: string | null
  provider?: string
  emailVerified?: boolean
  lastLoginAt?: string | null
}

export interface Org {
  id: string
  name: string
  plan: string
}

interface AuthContextValue {
  user: User | null
  org: Org | null
  token: string | null
  loading: boolean
  sessionExpires?: string
  loginWithGoogle: () => Promise<void>
  loginWithDemo: (email: string) => Promise<void>
  logout: () => Promise<void>
  setRole: (role: RoleId) => void
  roleLabel: string
  roleDef: (typeof ROLES)[number] | undefined
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  org: null,
  token: null,
  loading: true,
  loginWithGoogle: async () => {},
  loginWithDemo: async () => {},
  logout: async () => {},
  setRole: () => {},
  roleLabel: "Security Admin",
  roleDef: undefined,
})

function getStoredRole(): RoleId | null {
  if (typeof window === "undefined") return null
  const r = localStorage.getItem("sentinelx-role")
  return r && ROLES.some((d) => d.id === r) ? (r as RoleId) : null
}

function AuthConsumer({ children }: { children: React.ReactNode }) {
  const { data, status, update } = useSession()
  const [role, setRoleState] = useState<RoleId | null>(null)

  useEffect(() => {
    if (data?.accessToken) {
      setAuthToken(data.accessToken)
    } else {
      setAuthToken(null)
    }
  }, [data?.accessToken])

  useEffect(() => {
    const stored = getStoredRole()
    if (stored) setRoleState(stored)
    const handler = () => {
      const r = getStoredRole()
      if (r) setRoleState(r)
    }
    window.addEventListener("sentinelx-role-change", handler)
    window.addEventListener("storage", handler)
    return () => {
      window.removeEventListener("sentinelx-role-change", handler)
      window.removeEventListener("storage", handler)
    }
  }, [])

  const sessionUser = data?.user
  const user = useMemo<User | null>(() => {
    if (!sessionUser) return null
    return {
      id: sessionUser.id,
      email: sessionUser.email,
      name: sessionUser.name,
      role: sessionUser.role,
      picture: sessionUser.picture,
    }
  }, [sessionUser])

  const loginWithGoogle = useCallback(async () => {
    const res = await signIn("google", { callbackUrl: "/dashboard", redirect: false })
    if (res?.error) throw new Error(res.error)
    if (res?.url) {
      if (res.url.includes("error=") || res.url.includes("/login")) {
        throw new Error(res.error ?? "Google sign-in is not configured on the server")
      }
      window.location.href = res.url
    }
  }, [])

  const loginWithDemo = useCallback(async (email: string) => {
    const result = await signIn("credentials", { email, redirect: false })
    if (result?.error) {
      throw new Error("Login failed")
    }
    await update()
  }, [update])

  const logout = useCallback(async () => {
    await signOut({ callbackUrl: "/login" })
  }, [])

  const handleSetRole = useCallback((next: RoleId) => {
    localStorage.setItem("sentinelx-role", next)
    window.dispatchEvent(new Event("sentinelx-role-change"))
    setRoleState(next)
  }, [])

  const value = useMemo(() => {
    const effectiveRole = role ?? (user?.role as RoleId | undefined) ?? null
    const roleDef = effectiveRole ? ROLES.find((r) => r.id === effectiveRole) : undefined
    return {
      user,
      org: (data?.org as Org | null) ?? null,
      token: data?.accessToken ?? null,
      loading: status === "loading",
      sessionExpires: data?.expires,
      loginWithGoogle,
      loginWithDemo,
      logout,
      setRole: handleSetRole,
      roleLabel: roleDef?.label ?? "Security Admin",
      roleDef,
    }
  }, [user, data, status, role, loginWithGoogle, loginWithDemo, logout, handleSetRole])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AuthConsumer>{children}</AuthConsumer>
    </SessionProvider>
  )
}

export function useAuth(): AuthContextValue {
  return useContext(AuthContext)
}