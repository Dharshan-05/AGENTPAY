import { v2 as cloudinary } from "cloudinary"
import type { UploadApiResponse, UploadApiOptions, ResourceApiResponse } from "cloudinary"

const CLOUDINARY_CLOUD_NAME = process.env.CLOUDINARY_CLOUD_NAME
const CLOUDINARY_API_KEY = process.env.CLOUDINARY_API_KEY
const CLOUDINARY_API_SECRET = process.env.CLOUDINARY_API_SECRET

let configured = false

if (CLOUDINARY_CLOUD_NAME && CLOUDINARY_API_KEY && CLOUDINARY_API_SECRET) {
  cloudinary.config({
    cloud_name: CLOUDINARY_CLOUD_NAME,
    api_key: CLOUDINARY_API_KEY,
    api_secret: CLOUDINARY_API_SECRET,
    secure: true,
  })
  configured = true
  console.log("[Cloudinary] Configured")
} else {
  console.log("[Cloudinary] Not configured — running in demo mode")
}

export function isCloudinaryConfigured(): boolean {
  return configured
}

export interface UploadResult {
  publicId: string
  url: string
  secureUrl: string
  format: string
  width?: number
  height?: number
  bytes: number
  createdAt: string
}

export async function uploadFile(
  file: Buffer | string,
  options: {
    folder?: string
    publicId?: string
    resourceType?: "auto" | "image" | "raw" | "video"
    tags?: string[]
    context?: Record<string, string>
  } = {}
): Promise<UploadResult | null> {
  if (!configured) {
    // Demo mode - return mock result
    const mockId = `demo-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    return {
      publicId: mockId,
      url: `https://demo.cloudinary.com/${mockId}`,
      secureUrl: `https://demo.cloudinary.com/${mockId}`,
      format: "pdf",
      bytes: file instanceof Buffer ? file.length : 1024,
      createdAt: new Date().toISOString(),
    }
  }

  try {
    const result = await new Promise<UploadApiResponse>((resolve, reject) => {
      const uploadOptions: UploadApiOptions = {
        folder: options.folder ?? "sentinelx",
        resource_type: options.resourceType ?? "auto",
        tags: options.tags ?? [],
        context: options.context ?? {},
      }
      if (options.publicId) uploadOptions.public_id = options.publicId

      if (typeof file === "string") {
        cloudinary.uploader.upload(file, uploadOptions, (err, result) => {
          if (err) reject(err)
          else if (result) resolve(result)
          else reject(new Error("Cloudinary upload returned no result"))
        })
      } else {
        cloudinary.uploader.upload_stream(uploadOptions, (err, result) => {
          if (err) reject(err)
          else if (result) resolve(result)
          else reject(new Error("Cloudinary upload returned no result"))
        }).end(file)
      }
    })

    return {
      publicId: result.public_id,
      url: result.url,
      secureUrl: result.secure_url,
      format: result.format,
      width: result.width,
      height: result.height,
      bytes: result.bytes,
      createdAt: result.created_at,
    }
  } catch (error) {
    console.error("[Cloudinary] Upload failed:", error)
    return null
  }
}

export async function uploadPDF(
  buffer: Buffer,
  filename: string,
  metadata: { incidentId?: string; reportType?: string; userId?: string } = {}
): Promise<UploadResult | null> {
  return uploadFile(buffer, {
    folder: "sentinelx/compliance-reports",
    publicId: filename.replace(/\.pdf$/i, ""),
    resourceType: "raw",
    tags: ["compliance", "report", metadata.reportType].filter((t): t is string => Boolean(t)),
    context: {
      incidentId: metadata.incidentId ?? "",
      reportType: metadata.reportType ?? "",
      userId: metadata.userId ?? "",
    },
  })
}

export async function uploadEvidence(
  buffer: Buffer,
  filename: string,
  metadata: { incidentId: string; evidenceType: string; userId?: string } = {
    incidentId: "",
    evidenceType: "screenshot",
  }
): Promise<UploadResult | null> {
  return uploadFile(buffer, {
    folder: "sentinelx/evidence",
    publicId: `incident-${metadata.incidentId}-${filename.replace(/\.[^/.]+$/, "")}`,
    resourceType: "auto",
    tags: ["evidence", metadata.evidenceType, `incident-${metadata.incidentId}`],
    context: {
      incidentId: metadata.incidentId,
      evidenceType: metadata.evidenceType,
      userId: metadata.userId ?? "",
    },
  })
}

export async function uploadAvatar(buffer: Buffer, userId: string): Promise<UploadResult | null> {
  return uploadFile(buffer, {
    folder: "sentinelx/avatars",
    publicId: `user-${userId}`,
    resourceType: "image",
    tags: ["avatar", `user-${userId}`],
  })
}

export async function deleteFile(publicId: string): Promise<boolean> {
  if (!configured) return true

  try {
    await new Promise<void>((resolve, reject) => {
      cloudinary.uploader.destroy(publicId, (err) => {
        if (err) reject(err)
        else resolve()
      })
    })
    return true
  } catch (error) {
    console.error("[Cloudinary] Delete failed:", error)
    return false
  }
}

export async function getFileInfo(publicId: string): Promise<UploadResult | null> {
  if (!configured) return null

  try {
    const result = await new Promise<UploadApiResponse | null>((resolve, reject) => {
      cloudinary.api.resource(publicId, (err, result) => {
        if (err) reject(err)
        else if (result) resolve(result)
        else resolve(null)
      })
    })
    if (!result) return null
    return {
      publicId: result.public_id,
      url: result.url,
      secureUrl: result.secure_url,
      format: result.format,
      width: result.width,
      height: result.height,
      bytes: result.bytes,
      createdAt: result.created_at,
    }
  } catch (error) {
    console.error("[Cloudinary] Get info failed:", error)
    return null
  }
}

export async function listFiles(folder: string, maxResults = 50): Promise<UploadResult[]> {
  if (!configured) return []

  try {
    const result = await new Promise<ResourceApiResponse | null>((resolve, reject) => {
      cloudinary.api.resources(
        {
          type: "upload",
          prefix: folder,
          max_results: maxResults,
        },
        (err, result) => {
          if (err) reject(err)
          else if (result) resolve(result)
          else resolve(null)
        }
      )
    })
    if (!result) return []
    return result.resources.map((r) => ({
      publicId: r.public_id,
      url: r.url,
      secureUrl: r.secure_url,
      format: r.format,
      width: r.width,
      height: r.height,
      bytes: r.bytes,
      createdAt: r.created_at,
    }))
  } catch (error) {
    console.error("[Cloudinary] List failed:", error)
    return []
  }
}

export function getSignedUrl(publicId: string, expiresInSeconds = 3600): string {
  if (!configured) return `https://demo.cloudinary.com/${publicId}`

  return cloudinary.utils.private_download_url(publicId, "raw", {
    expires_at: Math.floor(Date.now() / 1000) + expiresInSeconds,
  })
}

export function healthCheck(): { configured: boolean; cloudName?: string; error?: string } {
  if (!configured) {
    return { configured: false, error: "Not configured" }
  }
  return { configured: true, cloudName: CLOUDINARY_CLOUD_NAME }
}