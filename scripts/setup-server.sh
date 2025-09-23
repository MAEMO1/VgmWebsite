#!/bin/bash

# VGM Server Setup Script
# Installeert alle benodigde software op de Hostinger VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Starting VGM server setup..."

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
print_status "Installing Docker..."
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
print_status "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
print_status "Adding user to docker group..."
sudo usermod -aG docker $USER

# Install Git
print_status "Installing Git..."
sudo apt install -y git

# Install additional tools
print_status "Installing additional tools..."
sudo apt install -y curl wget htop nano vim ufw

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create application directories
print_status "Creating application directories..."
sudo mkdir -p /opt/vgm-production
sudo mkdir -p /opt/vgm-staging
sudo chown $USER:$USER /opt/vgm-production
sudo chown $USER:$USER /opt/vgm-staging

# Clone repository
print_status "Cloning VGM repository..."
cd /opt/vgm-production
git clone https://github.com/MAEMO1/VgmWebsite.git .

# Set up environment files
print_status "Setting up environment files..."
cat > .env.production << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/vgm

# Security
SESSION_SECRET=$(openssl rand -hex 32)
FLASK_ENV=production

# Redis
REDIS_URL=redis://redis:6379/0

# External API Keys (add your keys here)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@vgmgent.be
EOF

# Create staging environment
cd /opt/vgm-staging
git clone https://github.com/MAEMO1/VgmWebsite.git .

cat > .env.staging << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres-staging:5432/vgm_staging

# Security
SESSION_SECRET=$(openssl rand -hex 32)
FLASK_ENV=staging

# Redis
REDIS_URL=redis://redis-staging:6379/0

# External API Keys (add your keys here)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@staging.vgmgent.be
EOF

# Generate SSH key for GitHub Actions
print_status "Generating SSH key for GitHub Actions..."
ssh-keygen -t rsa -b 4096 -f ~/.ssh/vgm_deploy_key -N ""

# Display SSH public key
print_success "SSH key generated!"
echo ""
print_status "Add this SSH public key to your GitHub repository:"
echo "=================================="
cat ~/.ssh/vgm_deploy_key.pub
echo "=================================="
echo ""
print_status "Add this SSH private key to GitHub Secrets as STAGING_SSH_KEY and PRODUCTION_SSH_KEY:"
echo "=================================="
cat ~/.ssh/vgm_deploy_key
echo "=================================="

# Display server IP
print_status "Your server IP address:"
curl -s ifconfig.me
echo ""

print_success "Server setup completed!"
print_status "Next steps:"
print_status "1. Add the SSH public key to your GitHub repository"
print_status "2. Add the SSH private key to GitHub Secrets"
print_status "3. Update GitHub Secrets with your server IP"
print_status "4. Run: ./scripts/deploy-advanced.sh -e staging"
