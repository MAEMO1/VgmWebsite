#!/bin/bash

# VGM Vercel Deployment Script
# Dit script helpt bij het deployen van de VGM frontend naar Vercel

set -e

echo "🚀 VGM Vercel Deployment Script"
echo "================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Installing..."
    npm install -g vercel
fi

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo "📦 Installing dependencies..."
pnpm install

echo "🔧 Building project..."
pnpm build

echo "🌐 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment completed!"
echo "🔗 Check your Vercel dashboard for the deployment URL"
