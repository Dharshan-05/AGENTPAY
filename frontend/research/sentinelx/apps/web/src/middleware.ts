import { auth } from "@/lib/auth-config"
import { NextResponse } from "next/server"

export default auth((req) => {
  const isLoggedIn = !!req.auth
  const isLoginPage = req.nextUrl.pathname.startsWith("/login")
  const isApiRoute = req.nextUrl.pathname.startsWith("/api")
  const isPublicRoute = req.nextUrl.pathname === "/" || 
    req.nextUrl.pathname.startsWith("/_next") || 
    req.nextUrl.pathname.startsWith("/favicon") || 
    req.nextUrl.pathname.startsWith("/manifest") || 
    req.nextUrl.pathname.startsWith("/pricing") ||
    req.nextUrl.pathname.startsWith("/signup") ||
    req.nextUrl.pathname.startsWith("/legal/") ||
    req.nextUrl.pathname.startsWith("/contact") ||
    req.nextUrl.pathname.startsWith("/support") ||
    req.nextUrl.pathname.startsWith("/offline") ||
    req.nextUrl.pathname.startsWith("/maintenance") ||
    req.nextUrl.pathname === "/robots.txt" ||
    req.nextUrl.pathname === "/sitemap.xml" ||
    req.nextUrl.pathname === "/manifest.webmanifest" ||
    req.nextUrl.pathname === "/401" ||
    req.nextUrl.pathname === "/403" ||
    req.nextUrl.pathname === "/404" ||
    req.nextUrl.pathname === "/500"

  if (isApiRoute || isPublicRoute) {
    return NextResponse.next()
  }

  if (isLoginPage) {
    if (isLoggedIn) {
      return NextResponse.redirect(new URL("/dashboard", req.nextUrl))
    }
    return NextResponse.next()
  }

  if (!isLoggedIn) {
    const loginUrl = new URL("/login", req.nextUrl)
    loginUrl.searchParams.set("callbackUrl", req.nextUrl.pathname)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
})

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|login|public).*)",
  ],
}