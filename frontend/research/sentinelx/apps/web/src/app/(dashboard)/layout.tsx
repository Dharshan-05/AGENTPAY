"use client"

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { MotionConfig, motion } from "framer-motion";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { StatusBar } from "@/components/layout/status-bar";
import { LiveNotifications } from "@/components/layout/live-notifications";
import { Toaster } from "@/components/ui/toast";
import { RoleProvider } from "@/components/layout/role-context";
import { cn } from "@/lib/utils";

const SHORTCUTS: Record<string, string> = {
  x: "/executive",
  d: "/dashboard",
  o: "/soc",
  s: "/scanner",
  w: "/twin",
  i: "/intelligence",
  q: "/explain",
  y: "/analytics",
  c: "/copilot",
  p: "/demo",
  t: "/threats",
  a: "/activity",
  l: "/policies",
  e: "/agents",
  u: "/audit",
  r: "/reports",
  m: "/compliance",
  n: "/system",
  k: "/settings",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const read = () => setCollapsed(localStorage.getItem("sentinelx-sidebar") === "true");
    read();
    window.addEventListener("sentinelx-sidebar-change", read);
    window.addEventListener("storage", read);
    return () => {
      window.removeEventListener("sentinelx-sidebar-change", read);
      window.removeEventListener("storage", read);
    };
  }, []);

  useEffect(() => {
    let pending = "";
    let timer: ReturnType<typeof setTimeout> | null = null;

    const handler = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      const key = e.key.toLowerCase();
      if (key === "g") {
        pending = "g";
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => (pending = ""), 600);
        return;
      }
      if (pending === "g" && SHORTCUTS[key]) {
        e.preventDefault();
        pending = "";
        if (timer) clearTimeout(timer);
        router.push(SHORTCUTS[key]);
      }
    };
    window.addEventListener("keydown", handler);
    return () => {
      window.removeEventListener("keydown", handler);
      if (timer) clearTimeout(timer);
    };
  }, [router]);

  return (
    <MotionConfig reducedMotion="user">
      <RoleProvider>
        <Toaster />
        <LiveNotifications />
        <div className="min-h-screen">
          <Sidebar />
          <div
            className={cn(
              "flex min-h-screen flex-col transition-all duration-300",
              collapsed ? "pl-[72px]" : "pl-[260px]",
            )}
          >
            <Header />
            <main className="mx-auto w-full max-w-[1440px] flex-1 px-6 py-6 pb-14">
              <motion.div
                key="page-shell"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
              >
                {children}
              </motion.div>
            </main>
          </div>
          <StatusBar />
        </div>
      </RoleProvider>
    </MotionConfig>
  );
}