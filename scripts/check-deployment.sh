#!/bin/bash

# VGM Deployment Check Script
# Dit script controleert of de deployment succesvol is

set -e

echo "🔍 VGM Deployment Check Script"
echo "=============================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed. Please install it first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo "📊 Checking Vercel project status..."
vercel ls

echo ""
echo "🌐 Checking deployment URLs..."
vercel inspect --prod

echo ""
echo "🔧 Checking environment variables..."
vercel env ls

echo ""
echo "📈 Checking analytics..."
vercel analytics

echo ""
echo "✅ Deployment check completed!"
echo "🔗 Check your Vercel dashboard for more details"
