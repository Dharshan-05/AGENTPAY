# SentinelX API - Railway Deployment Guide

## Prerequisites
- Railway account with active plan (trial expired - need paid plan)
- MongoDB Atlas cluster (or PostgreSQL provider)
- Upstash Redis instance
- All API keys for integrations (OpenRouter, Razorpay, etc.)

## Quick Deploy Commands

```bash
# 1. Login to Railway (if not already)
railway login

# 2. Initialize project in the repo root
railway init

# 3. Set environment variables (use the .env.production.example as reference)
railway variables set NODE_ENV=production
railway variables set PORT=3001
railway variables set HOST=0.0.0.0
railway variables set WEB_ORIGIN=https://sentinel--ai.vercel.app
railway variables set DATABASE_URL="postgresql://..."
railway variables set REDIS_URL="redis://..."
railway variables set JWT_SECRET="..."
railway variables set NEXTAUTH_SECRET="..."
railway variables set GOOGLE_CLIENT_ID="..."
railway variables set GOOGLE_CLIENT_SECRET="..."
railway variables set OPENROUTER_API_KEY="..."
railway variables set RAZORPAY_KEY_ID="..."
railway variables set RAZORPAY_KEY_SECRET="..."
railway variables set RAZORPAY_WEBHOOK_SECRET="..."
# ... set all other variables from .env.production.example

# 4. Deploy
railway up

# 5. Get the production URL
railway domain

# 6. Update Vercel web app with the API URL
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-api.railway.app

# 7. Redeploy web
vercel --prod --yes
```

## Required Environment Variables

See `apps/api/.env.production.example` for the complete list.

### Critical Variables (must be set):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `WEB_ORIGIN` - `https://sentinel--ai.vercel.app`
- `JWT_SECRET` - Secure random string (32+ chars)
- `NEXTAUTH_SECRET` - Same as web app
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - From Google Cloud Console
- `OPENROUTER_API_KEY` - For AI features
- `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` / `RAZORPAY_WEBHOOK_SECRET` - For billing

### Optional Variables:
- `SENTRY_DSN`, `POSTHOG_API_KEY`, `CLOUDINARY_*`, `RESEND_API_KEY`, `SLACK_WEBHOOK_URL`

## Post-Deployment Verification

```bash
# 1. Check health endpoint
curl https://your-api.railway.app/api/health

# 2. Test CORS
curl -H "Origin: https://sentinel--ai.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type, Authorization" \
     -X OPTIONS https://your-api.railway.app/api/health

# 3. Test auth endpoint
curl -X POST https://your-api.railway.app/api/auth/google \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sentinelx.dev"}'

# 4. Update web app
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-api.railway.app

# 5. Redeploy web
vercel --prod --yes
```

## Troubleshooting

### CORS Issues
- Ensure `WEB_ORIGIN` matches exactly: `https://sentinel--ai.vercel.app`
- Check that `credentials: true` is set in Fastify CORS config

### Database Connection
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:5432/db?sslmode=require`
- Ensure MongoDB Atlas allows connections from Railway IPs (0.0.0.0/0)

### Redis Connection
- Verify `REDIS_URL` format: `redis://default:password@host:port`
- For Upstash: Use REST URL and token if preferred

### Google OAuth
- Add `https://your-api.railway.app/api/auth/callback/google` to authorized redirect URIs in Google Cloud Console
- Also add `https://sentinel--ai.vercel.app/api/auth/callback/google` for web app

### WebSocket/Socket.IO
- Ensure Railway supports WebSockets (it does)
- Check that Socket.IO CORS origin matches `WEB_ORIGIN`

## Health Check Endpoint

GET `/api/health` returns:
```json
{
  "status": "ok",
  "service": "sentinelx-api",
  "version": "1.0.0",
  "mode": "connected|memory",
  "uptimeSeconds": 123,
  "timestamp": "2026-08-07T...",
  "checks": {
    "database": { "mode": "connected", "available": true },
    "redis": true,
    "llm": 2
  },
  "providers": [...]
}
```