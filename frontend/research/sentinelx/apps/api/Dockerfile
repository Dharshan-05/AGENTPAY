# Dockerfile for Railway Deployment
# Multi-stage build for optimal production image

# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/ ./src/
COPY prisma/ ./prisma/

# Generate Prisma client
RUN npx prisma generate

# Build TypeScript
RUN npm run build

# Production stage
FROM node:22-alpine AS production

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S sentinelx -u 1001 -G nodejs

# Copy built files
COPY --from=builder --chown=sentinelx:nodejs /app/dist ./dist
COPY --from=builder --chown=sentinelx:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=sentinelx:nodejs /app/package.json ./
COPY --from=builder --chown=sentinelx:nodejs /app/prisma ./prisma

# Switch to non-root user
USER sentinelx

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3001/api/health || exit 1

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "dist/server.js"]