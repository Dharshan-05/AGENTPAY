# SentinelX API - Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Railway Account Setup
- [ ] Railway account created
- [ ] Railway CLI installed (`npm install -g @railway/cli`)
- [ ] Logged into Railway (`railway login`)
- [ ] Project created (`railway init`)

### 2. Environment Variables (Set in Railway Dashboard)

#### Core Application
- [ ] `NODE_ENV=production`
- [ ] `PORT=3001`
- [ ] `WEB_ORIGIN=https://sentinelx.ai`

#### Database (MongoDB Atlas)
- [ ] `DATABASE_URL` / `MONGODB_URI`
  - Format: `mongodb+srv://username:password@cluster.mongodb.net/sentinelx?retryWrites=true&w=majority`
  - [ ] IP whitelist includes Railway IPs (0.0.0.0/0 for testing)
  - [ ] Database user has read/write permissions

#### Redis (Upstash)
- [ ] `UPSTASH_REDIS_REST_URL` (e.g., `https://your-redis.upstash.io`)
- [ ] `UPSTASH_REDIS_REST_TOKEN` (from Upstash dashboard)

#### Authentication & Security
- [ ] `JWT_SECRET` (min 32 chars, generate with `openssl rand -base64 32`)
- [ ] `COOKIE_SECRET` (min 32 chars, generate with `openssl rand -base64 32`)

#### OpenRouter (Primary LLM)
- [ ] `OPENROUTER_API_KEY` (from openrouter.ai)
- [ ] `OPENROUTER_DEFAULT_MODEL` (e.g., `nvidia/nemotron-3-ultra`)
- [ ] `OPENROUTER_FALLBACK_MODEL` (e.g., `nvidia/nemotron-3-super`)
- [ ] `OPENROUTER_SECONDARY_MODEL` (e.g., `openai/gpt-oss-20b`)

#### Google OAuth
- [ ] `GOOGLE_CLIENT_ID` (from Google Cloud Console)
- [ ] `GOOGLE_CLIENT_SECRET` (from Google Cloud Console)
- [ ] Authorized redirect URI: `https://sentinelx.ai/api/auth/callback/google`
- [ ] `NEXTAUTH_SECRET` (generate with `openssl rand -base64 32`)
- [ ] `NEXTAUTH_URL=https://sentinelx.ai`

#### Razorpay (Billing)
- [ ] `RAZORPAY_KEY_ID` (from Razorpay dashboard)
- [ ] `RAZORPAY_KEY_SECRET` (from Razorpay dashboard)
- [ ] `RAZORPAY_WEBHOOK_SECRET` (from Razorpay webhook settings)

#### Cloudinary (Media)
- [ ] `CLOUDINARY_CLOUD_NAME`
- [ ] `CLOUDINARY_API_KEY`
- [ ] `CLOUDINARY_API_SECRET`

#### Email (Resend)
- [ ] `RESEND_API_KEY` (from Resend dashboard)
- [ ] Domain verified in Resend

#### Slack (Notifications)
- [ ] `SLACK_WEBHOOK_URL` (from Slack app settings)

#### Analytics & Monitoring
- [ ] `POSTHOG_KEY` (from PostHog project settings)
- [ ] `SENTRY_DSN` (from Sentry project settings)

#### Web Origin
- [ ] `WEB_ORIGIN=https://sentinelx.ai`

#### Pipeline Settings (Optional)
- [ ] `PIPELINE_PACE_MS=240`
- [ ] `PIPELINE_PACE_JITTER_MS=220`
- [ ] `AI_REWRITE=1`
- [ ] `ADAPTIVE_RISK_AI=1`
- [ ] `LLM_SILENT=0`

#### Web Origin
- [ ] `WEB_ORIGIN=https://sentinelx.ai`

---

## Deployment Steps

### 1. Initial Setup
```bash
cd apps/api
chmod +x deploy-railway.sh
./deploy-railway.sh
```

### 2. Manual Railway Dashboard Configuration
1. Go to Railway dashboard
2. Select your project
3. Go to Variables tab
4. Add all environment variables from checklist above
5. Save and redeploy

### 3. Verify Deployment
```bash
# Check deployment status
railway status

# View logs
railway logs

# Open deployment URL
railway open
```

---

## Post-Deployment Verification

### API Health Checks
```bash
# Health endpoint
curl https://your-app.railway.app/api/health

# OpenRouter health
curl https://your-app.railway.app/api/openrouter/health

# OpenRouter metrics
curl https://your-app.railway.app/api/openrouter/metrics

# Dashboard data
curl https://your-app.railway.app/api/dashboard

# Executive dashboard
curl https://your-app.railway.app/api/executive
```

### Expected Health Response
```json
{
  "status": "ok",
  "service": "sentinelx-api",
  "version": "1.0.0",
  "mode": "connected",
  "uptimeSeconds": 123,
  "timestamp": "2026-08-07T...",
  "checks": {
    "database": { "mode": "connected", "available": true },
    "redis": true,
    "llm": 5
  },
  "providers": [
    { "id": "openrouter", "configured": true },
    { "id": "openai", "configured": false },
    ...
  ]
}
```

---

## Post-Deployment Smoke Tests

### 1. Web App Integration
- [ ] Update `NEXT_PUBLIC_API_URL` in web app to Railway URL
- [ ] Redeploy web app
- [ ] Test login flow
- [ ] Test AI scan
- [ ] Test OpenRouter failover

### 2. End-to-End Tests
- [ ] Login with Google OAuth
- [ ] Submit prompt through scanner
- [ ] Verify OpenRouter response
- [ ] Test OpenRouter failover (simulate failure)
- [ ] Check Executive Security Center loads
- [ ] Check AI Analytics page
- [ ] Check Judge Mode pipeline
- [ ] Test billing page
- [ ] Test notifications
- [ ] Test logout

### 3. Health Checks
- [ ] API health returns 200 OK
- [ ] MongoDB connection works
- [ ] Redis connection works
- [ ] OpenRouter configured
- [ ] Google OAuth works
- [ ] Razorpay webhooks work
- [ ] Slack notifications work
- [ ] Resend emails work
- [ ] PostHog tracking works
- [ ] Sentry error tracking works

---

## Rollback Plan
If deployment fails:
1. Check Railway logs: `railway logs`
2. Check environment variables
3. Revert to previous deployment in Railway dashboard
4. Check MongoDB Atlas IP whitelist
5. Check Upstash Redis connection

---

## Go/No-Go Criteria

### ✅ Go Criteria
- [ ] All environment variables set
- [ ] API health returns 200 OK
- [ ] MongoDB connected
- [ ] Redis connected
- [ ] OpenRouter configured
- [ ] Google OAuth works
- [ ] All smoke tests pass
- [ ] No TypeScript errors
- [ ] Build succeeds

### ❌ No-Go Criteria
- [ ] Any critical environment variable missing
- [ ] API health returns 500
- [ ] Database connection fails
- [ ] Redis connection fails
- [ ] Build fails
- [ ] TypeScript errors present

---

## Emergency Contacts
- Railway Support: https://railway.app/support
- MongoDB Atlas Support: https://support.mongodb.com/
- Upstash Support: https://upstash.com/support
- OpenRouter Support: https://openrouter.ai/support

---

## Notes
- Railway provides automatic HTTPS
- Railway provides custom domains (configure in Settings > Domains)
- Railway provides automatic rollbacks on health check failures
- Monitor costs in Railway dashboard (usage-based pricing)
- Set up alerts for high error rates or downtime

---

*Last Updated: August 7, 2026*
*Version: 1.0.0*