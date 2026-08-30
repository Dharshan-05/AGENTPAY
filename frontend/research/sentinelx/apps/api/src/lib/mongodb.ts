import { MongoClient, Db, Collection, type MongoClientOptions } from "mongodb"

const MONGODB_URI = process.env.MONGODB_URI || ""
const MONGODB_DB = process.env.MONGODB_DB || "sentinelx"

interface MongoCollections {
  users: Collection<Document>
  organizations: Collection<Document>
  auditLogs: Collection<Document>
  incidents: Collection<Document>
  policies: Collection<Document>
  reports: Collection<Document>
  sessions: Collection<Document>
  notifications: Collection<Document>
}

let client: MongoClient | null = null
let db: Db | null = null
let collections: MongoCollections | null = null
let connectionPromise: Promise<void> | null = null
let isConnected = false

export async function connectMongoDB(): Promise<void> {
  if (connectionPromise) return connectionPromise
  if (!MONGODB_URI) {
    console.log("[MongoDB] MONGODB_URI not set — skipping Atlas connection")
    return
  }

  connectionPromise = (async () => {
    try {
      const options: MongoClientOptions = {
        maxPoolSize: 10,
        minPoolSize: 2,
        maxIdleTimeMS: 30000,
        serverSelectionTimeoutMS: 5000,
        socketTimeoutMS: 45000,
        connectTimeoutMS: 10000,
      }

      client = new MongoClient(MONGODB_URI, options)
      await client.connect()
      db = client.db(MONGODB_DB)

      // Initialize collections
      collections = {
        users: db.collection("users"),
        organizations: db.collection("organizations"),
        auditLogs: db.collection("audit_logs"),
        incidents: db.collection("incidents"),
        policies: db.collection("policies"),
        reports: db.collection("reports"),
        sessions: db.collection("sessions"),
        notifications: db.collection("notifications"),
      }

      // Create indexes
      await createIndexes()

      isConnected = true
      console.log("[MongoDB] Connected to Atlas")
    } catch (error) {
      isConnected = false
      console.error("[MongoDB] Connection failed:", error)
      throw error
    }
  })()

  return connectionPromise
}

async function createIndexes(): Promise<void> {
  if (!collections) return

  try {
    await Promise.all([
      collections.users.createIndex({ email: 1 }, { unique: true }),
      collections.auditLogs.createIndex({ timestamp: -1 }),
      collections.auditLogs.createIndex({ userId: 1, timestamp: -1 }),
      collections.auditLogs.createIndex({ riskScore: -1 }),
      collections.incidents.createIndex({ status: 1, severity: -1, createdAt: -1 }),
      collections.incidents.createIndex({ assigneeId: 1, status: 1 }),
      collections.sessions.createIndex({ active: 1, startedAt: -1 }),
      collections.notifications.createIndex({ userId: 1, read: 1, createdAt: -1 }),
      collections.reports.createIndex({ createdAt: -1 }),
    ])
    console.log("[MongoDB] Indexes created")
  } catch (error) {
    console.warn("[MongoDB] Index creation warning:", error)
  }
}

export function getMongoDB(): Db | null {
  return db
}

export function getCollections(): MongoCollections | null {
  return collections
}

export function isMongoConnected(): boolean {
  return isConnected && client !== null
}

export async function closeMongoDB(): Promise<void> {
  if (client) {
    await client.close()
    client = null
    db = null
    collections = null
    isConnected = false
  }
}

// Health check
export async function mongoHealthCheck(): Promise<{ connected: boolean; latencyMs?: number; error?: string }> {
  if (!MONGODB_URI || !isConnected) {
    return { connected: false, error: "Not configured or not connected" }
  }
  try {
    const start = Date.now()
    await db?.command({ ping: 1 })
    return { connected: true, latencyMs: Date.now() - start }
  } catch (error) {
    return { connected: false, error: String(error) }
  }
}

// Collection helpers
export async function insertOne(collectionName: keyof MongoCollections, doc: any): Promise<string | null> {
  if (!collections) return null
  const result = await collections[collectionName].insertOne(doc)
  return result.insertedId.toString()
}

export async function findOne(collectionName: keyof MongoCollections, filter: any): Promise<any | null> {
  if (!collections) return null
  return collections[collectionName].findOne(filter)
}

export async function findMany(collectionName: keyof MongoCollections, filter: any, options?: { sort?: any; limit?: number; skip?: number }): Promise<any[]> {
  if (!collections) return []
  const cursor = collections[collectionName].find(filter)
  if (options?.sort) cursor.sort(options.sort)
  if (options?.skip) cursor.skip(options.skip)
  if (options?.limit) cursor.limit(options.limit)
  return cursor.toArray()
}

export async function countDocuments(collectionName: keyof MongoCollections, filter: any): Promise<number> {
  if (!collections) return 0
  return collections[collectionName].countDocuments(filter)
}

export async function updateOne(collectionName: keyof MongoCollections, filter: any, update: any): Promise<boolean> {
  if (!collections) return false
  const result = await collections[collectionName].updateOne(filter, update)
  return result.modifiedCount > 0
}

export async function deleteOne(collectionName: keyof MongoCollections, filter: any): Promise<boolean> {
  if (!collections) return false
  const result = await collections[collectionName].deleteOne(filter)
  return result.deletedCount > 0
}