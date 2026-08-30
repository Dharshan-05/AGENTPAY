import { io, type Socket } from "socket.io-client"
import type { AgentTraceEntry, PipelineResult } from "@/types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001"

let socket: Socket | null = null

export function getLiveSocket(): Socket {
  if (!socket) {
    socket = io(API_BASE, {
      transports: ["websocket", "polling"],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 5000,
    })
  }
  return socket
}

export function subscribeAgentUpdates(cb: (entry: AgentTraceEntry) => void): () => void {
  const s = getLiveSocket()
  s.on("agent:update", cb)
  return () => {
    s.off("agent:update", cb)
  }
}

export function subscribeScanComplete(cb: (result: PipelineResult) => void): () => void {
  const s = getLiveSocket()
  s.on("scan:complete", cb)
  return () => {
    s.off("scan:complete", cb)
  }
}

export interface LiveIncident {
  id: string;
  title: string;
  severity: string;
  department: string;
  riskScore: number;
}

export function subscribeIncidentNew(cb: (inc: LiveIncident) => void): () => void {
  const s = getLiveSocket()
  s.on("incident:new", cb)
  return () => {
    s.off("incident:new", cb)
  }
}

export function socketConnected(): boolean {
  return socket?.connected ?? false
}
