#!/bin/bash

# VGM Vercel Setup Script
# Dit script helpt bij het opzetten van een nieuw Vercel project

set -e

echo "🚀 VGM Vercel Setup Script"
echo "=========================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Navigate to frontend directory
cd frontend

echo "🔐 Logging in to Vercel..."
vercel login

echo "📁 Creating new Vercel project..."
vercel --yes

echo "⚙️  Configuring project settings..."
echo "Please configure the following in your Vercel dashboard:"
echo ""
echo "1. Go to Project Settings > Environment Variables"
echo "2. Add the following variables:"
echo "   - NEXT_PUBLIC_API_BASE_URL=https://your-backend-api.com"
echo "   - NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-google-maps-api-key"
echo "   - NEXT_PUBLIC_DEFAULT_LOCALE=nl"
echo "   - NEXT_PUBLIC_SUPPORTED_LOCALES=nl,en,fr,tr,ar,ps"
echo ""
echo "3. Go to Project Settings > Domains"
echo "4. Add your custom domain (e.g., vgm.be)"
echo ""
echo "5. Go to Project Settings > Git"
echo "6. Connect your GitHub repository"
echo ""
echo "✅ Setup completed!"
echo "🔗 Check your Vercel dashboard for the deployment URL"
