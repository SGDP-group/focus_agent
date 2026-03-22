#!/bin/bash

# Focus Agent EC2 Deployment Script
# This script sets up and deploys the Focus Agent on an EC2 instance

set -e

echo "🚀 Starting Focus Agent deployment to EC2..."

# Configuration
APP_NAME="focus-agent"
APP_DIR="/opt/$APP_NAME"
SERVICE_NAME="focus-agent"
NGINX_CONFIG="/etc/nginx/sites-available/$APP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use sudo)"
   exit 1
fi

# Update system packages
log_info "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
log_info "Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx curl software-properties-common

# Create application directory
log_info "Creating application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Copy application files (assumes script is run from project root)
log_info "Copying application files..."
if [ -f "../server.py" ]; then
    cp -r ../* .
else
    log_error "Please run this script from the project directory"
    exit 1
fi

# Create Python virtual environment
log_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
log_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file
log_info "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || cat > .env << EOF
# Required - Groq API key for the LLM
GROQ_API_KEY=your_groq_api_key_here

# Optional - LangSmith API key for tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
EOF
    log_warn "Please update .env file with your API keys"
fi

# Set proper permissions
log_info "Setting proper permissions..."
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# Create systemd service
log_info "Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Focus Agent API Service
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
log_info "Configuring Nginx reverse proxy..."
cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for streaming
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable Nginx site
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t || {
    log_error "Nginx configuration test failed"
    exit 1
}

# Enable and start services
log_info "Enabling and starting services..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME
systemctl enable nginx
systemctl restart nginx

# Setup firewall
log_info "Configuring firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# Wait for service to start
sleep 5

# Check service status
if systemctl is-active --quiet $SERVICE_NAME; then
    log_info "✅ Focus Agent service is running successfully!"
else
    log_error "❌ Focus Agent service failed to start"
    systemctl status $SERVICE_NAME
    exit 1
fi

# Get instance IP
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "   • Application URL: http://$INSTANCE_IP"
echo "   • API Documentation: http://$INSTANCE_IP/docs"
echo "   • Health Check: http://$INSTANCE_IP/health"
echo "   • Service Status: systemctl status $SERVICE_NAME"
echo "   • Logs: journalctl -u $SERVICE_NAME -f"
echo ""
echo "⚠️  Important:"
echo "   • Update .env file with your GROQ_API_KEY"
echo "   • Configure SSL certificate for production use"
echo "   • Set up proper domain name and DNS records"
echo ""
echo "🔧 Useful Commands:"
echo "   • Restart service: sudo systemctl restart $SERVICE_NAME"
echo "   • View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "   • Update app: cd $APP_DIR && git pull && sudo systemctl restart $SERVICE_NAME"
echo ""
