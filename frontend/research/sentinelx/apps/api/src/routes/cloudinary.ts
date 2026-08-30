import type { FastifyInstance } from "fastify"
import { uploadFile, uploadPDF, uploadEvidence, uploadAvatar, deleteFile, listFiles, getSignedUrl, healthCheck } from "../lib/cloudinary"
import { authMiddleware } from "../lib/auth"

export async function registerCloudinaryRoutes(app: FastifyInstance): Promise<void> {
  app.get("/api/cloudinary/health", { preHandler: authMiddleware }, async () => {
    return healthCheck()
  })

  app.post("/api/cloudinary/upload", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      file?: string // base64
      folder?: string
      publicId?: string
      resourceType?: "auto" | "image" | "raw" | "video"
      tags?: string[]
    }

    if (!body.file) {
      return reply.code(400).send({ error: "File (base64) is required" })
    }

    const buffer = Buffer.from(body.file, "base64")
    const result = await uploadFile(buffer, {
      folder: body.folder,
      publicId: body.publicId,
      resourceType: body.resourceType,
      tags: body.tags,
    })

    if (!result) {
      return reply.code(500).send({ error: "Upload failed" })
    }

    return result
  })

  app.post("/api/cloudinary/upload/pdf", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      file: string // base64
      filename: string
      incidentId?: string
      reportType?: string
      userId?: string
    }

    if (!body.file || !body.filename) {
      return reply.code(400).send({ error: "File (base64) and filename are required" })
    }

    const buffer = Buffer.from(body.file, "base64")
    const result = await uploadPDF(buffer, body.filename, {
      incidentId: body.incidentId,
      reportType: body.reportType,
      userId: body.userId,
    })

    if (!result) {
      return reply.code(500).send({ error: "PDF upload failed" })
    }

    return result
  })

  app.post("/api/cloudinary/upload/evidence", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      file: string // base64
      filename: string
      incidentId: string
      evidenceType: string
      userId?: string
    }

    if (!body.file || !body.filename || !body.incidentId) {
      return reply.code(400).send({ error: "File, filename, and incidentId are required" })
    }

    const buffer = Buffer.from(body.file, "base64")
    const result = await uploadEvidence(buffer, body.filename, {
      incidentId: body.incidentId,
      evidenceType: body.evidenceType,
      userId: body.userId,
    })

    if (!result) {
      return reply.code(500).send({ error: "Evidence upload failed" })
    }

    return result
  })

  app.post("/api/cloudinary/upload/avatar", { preHandler: authMiddleware }, async (request, reply) => {
    const body = request.body as {
      file: string // base64
      userId: string
    }

    if (!body.file || !body.userId) {
      return reply.code(400).send({ error: "File (base64) and userId are required" })
    }

    const buffer = Buffer.from(body.file, "base64")
    const result = await uploadAvatar(buffer, body.userId)

    if (!result) {
      return reply.code(500).send({ error: "Avatar upload failed" })
    }

    return result
  })

  app.delete("/api/cloudinary/:publicId", { preHandler: authMiddleware }, async (request, reply) => {
    const { publicId } = request.params as { publicId: string }
    const success = await deleteFile(publicId)

    if (!success) {
      return reply.code(500).send({ error: "Delete failed" })
    }

    return { success: true }
  })

  app.get("/api/cloudinary/list", { preHandler: authMiddleware }, async (request) => {
    const query = request.query as { folder?: string; max?: string }
    const files = await listFiles(query.folder ?? "sentinelx", Number(query.max) ?? 50)
    return { files }
  })

  app.get("/api/cloudinary/signed-url", { preHandler: authMiddleware }, async (request) => {
    const query = request.query as { publicId: string; expires?: string }
    const url = getSignedUrl(query.publicId, Number(query.expires) ?? 3600)
    return { url }
  })
}