"use client"

let apiToken: string | null = null

export function setAuthToken(token: string | null) {
  apiToken = token
}

export function getApiToken(): string | null {
  return apiToken
}