#!/bin/bash
# Railway Deployment Script for SentinelX API
# Usage: ./deploy-railway.sh

set -e

echo "🚀 Deploying SentinelX API to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
fi

# Check if project exists
echo "📦 Checking Railway project..."
if ! railway project &> /dev/null; then
    echo "📦 Creating new Railway project..."
    railway init
fi

# Set environment variables
echo "🔧 Setting environment variables..."

# Core
railway variables set NODE_ENV=production
railway variables set PORT=3001
railway variables set WEB_ORIGIN=https://sentinelx.ai

# Database (to be filled by user)
echo "⚠️  Please set the following variables in Railway dashboard:"
echo "   DATABASE_URL / MONGODB_URI"
echo "   UPSTASH_REDIS_REST_URL"
echo "   UPSTASH_REDIS_REST_TOKEN"
echo "   JWT_SECRET"
echo "   COOKIE_SECRET"
echo "   OPENROUTER_API_KEY"
echo "   GOOGLE_CLIENT_ID"
echo "   GOOGLE_CLIENT_SECRET"
echo "   NEXTAUTH_SECRET"
echo "   NEXTAUTH_URL"
echo "   RAZORPAY_KEY_ID"
echo "   RAZORPAY_KEY_SECRET"
echo "   RAZORPAY_WEBHOOK_SECRET"
echo "   CLOUDINARY_CLOUD_NAME"
echo "   CLOUDINARY_API_KEY"
echo "   CLOUDINARY_API_SECRET"
echo "   RESEND_API_KEY"
echo "   SLACK_WEBHOOK_URL"
echo "   POSTHOG_KEY"
echo "   SENTRY_DSN"
echo "   WEB_ORIGIN=https://sentinelx.ai"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Show deployment URL
echo "✅ Deployment complete!"
railway status

echo ""
echo "🎉 Deployment complete!"
echo "📋 Next steps:"
echo "   1. Set all required environment variables in Railway dashboard"
echo "   2. Run 'railway open' to view your deployment"
echo "   3. Test the health endpoint: https://your-app.railway.app/api/health"
echo "   4. Update web app NEXT_PUBLIC_API_URL to point to Railway URL"