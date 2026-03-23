# EC2 Deployment Guide for Focus Agent

This guide provides step-by-step instructions for deploying the Focus Agent API to an AWS EC2 instance.

## Prerequisites

### AWS EC2 Instance
- **Instance Type**: t3.medium or larger (recommended for LLM processing)
- **AMI**: Ubuntu 22.04 LTS or Amazon Linux 2
- **Security Group**: Allow SSH (22), HTTP (80), HTTPS (443)
- **Storage**: At least 20GB SSD
- **Public IP**: Enable for direct access

### Local Requirements
- SSH access to the EC2 instance
- Project files uploaded to the instance

## Quick Deployment (Recommended)

Use the automated deployment script:

```bash
# 1. Upload project to EC2
scp -r /path/to/focus-agent ubuntu@your-ec2-ip:~/

# 2. SSH into EC2 instance
ssh ubuntu@your-ec2-ip

# 3. Navigate to project directory
cd focus-agent

# 4. Make deployment script executable
chmod +x deploy.sh

# 5. Run deployment script (requires sudo)
sudo ./deploy.sh
```

## Manual Deployment

If you prefer manual deployment, follow these steps:

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx curl

# Create application directory
sudo mkdir -p /opt/focus-agent
sudo chown $USER:$USER /opt/focus-agent
```

### 2. Application Setup

```bash
# Copy application files
sudo cp -r focus-agent/* /opt/focus-agent/
cd /opt/focus-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment
sudo cp .env.example .env  # or create manually
sudo nano .env  # Add your API keys
```

### 3. Service Configuration

```bash
# Install systemd service
sudo cp focus-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable focus-agent
sudo systemctl start focus-agent
```

### 4. Nginx Configuration

```bash
# Install Nginx configuration
sudo cp nginx-focus-agent.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/nginx-focus-agent.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Firewall Setup

```bash
# Configure firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

## Configuration

### Environment Variables

Create/update `/opt/focus-agent/.env`:

```env
# Required - Groq API key for the LLM
GROQ_API_KEY=your_groq_api_key_here

# Optional - LangSmith API key for tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
```

### Getting API Keys

- **Groq**: Sign up at [console.groq.com](https://console.groq.com/) and generate an API key
- **LangSmith** (optional): Sign up at [smith.langchain.com](https://smith.langchain.com/) for tracing

## Accessing Your Application

After deployment, your application will be available at:

- **Main API**: `http://your-ec2-ip/`
- **Documentation**: `http://your-ec2-ip/docs`
- **Health Check**: `http://your-ec2-ip/health`

## Testing the Deployment

```bash
# Health check
curl http://your-ec2-ip/health

# Test task breakdown endpoint
curl -X POST "http://your-ec2-ip/invoke-task-breakdown" \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a birthday party"}'

# Test helper endpoint
curl -X POST "http://your-ec2-ip/invoke_helper" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?"}'
```

## Management Commands

### Service Management

```bash
# Check service status
sudo systemctl status focus-agent

# View logs
sudo journalctl -u focus-agent -f

# Restart service
sudo systemctl restart focus-agent

# Stop service
sudo systemctl stop focus-agent
```

### Application Updates

```bash
# Update application
cd /opt/focus-agent
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart focus-agent
```

## Security Recommendations

### 1. SSL Certificate (Production)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Firewall Rules

```bash
# Restrict SSH access (optional)
sudo ufw limit 22

# Allow only specific IPs (optional)
sudo ufw allow from YOUR_IP to any port 22
```

### 3. Security Headers

The Nginx configuration includes security headers. For additional security:

```bash
# Fail2Ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## Monitoring and Troubleshooting

### Log Locations

- **Application logs**: `sudo journalctl -u focus-agent -f`
- **Nginx logs**: `/var/log/nginx/focus-agent-*.log`
- **System logs**: `/var/log/syslog`

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status focus-agent

# View detailed logs
sudo journalctl -u focus-agent -n 50
```

#### API Not Responding
```bash
# Check if application is running
curl http://localhost:8000/health

# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R www-data:www-data /opt/focus-agent
sudo chmod -R 755 /opt/focus-agent
```

## Performance Optimization

### 1. Instance Sizing

- **Development**: t3.micro (2GB RAM)
- **Production**: t3.medium (4GB RAM) or larger
- **High Traffic**: t3.large (8GB RAM) or m5.large

### 2. Application Tuning

Edit `/etc/systemd/system/focus-agent.service`:

```ini
# Add workers for better concurrency
ExecStart=/opt/focus-agent/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Nginx Optimization

Add to `nginx-focus-agent.conf`:

```nginx
# Add to server block
worker_processes auto;
worker_connections 1024;

# Add to location block
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;
```

## Backup and Recovery

### Application Backup

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/focus-agent"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/focus-agent-$DATE.tar.gz /opt/focus-agent
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh
sudo ./backup.sh
```

### Database Backup (if applicable)

If you add database persistence:

```bash
# Example for PostgreSQL
pg_dump focus_agent > backup_$(date +%Y%m%d).sql
```

## Scaling Considerations

### Horizontal Scaling

- Use AWS Elastic Load Balancer (ELB)
- Deploy multiple instances behind the load balancer
- Consider AWS ECS for containerized deployment

### Vertical Scaling

- Monitor CPU and memory usage
- Upgrade instance type as needed
- Consider using AWS Auto Scaling Groups

## Support

For deployment issues:

1. Check the logs using the commands above
2. Verify all configuration files are properly set
3. Ensure all required ports are open in security groups
4. Test API endpoints manually before using the application

## Cost Optimization

- Use instance types appropriate for your workload
- Consider reserved instances for long-term deployments
- Monitor CloudWatch metrics for usage patterns
- Set up billing alerts for cost control
