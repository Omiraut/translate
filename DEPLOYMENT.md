# DEPLOYMENT GUIDE

## Overview

This guide covers deploying the Translation API in various environments.

---

## Local Development

### Prerequisites
- Python 3.8+
- pip or virtualenv

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify dependencies
python check_dependencies.py

# Run the API
python main.py
```

The API will be available at: **http://localhost:8000**

---

## Production Deployment

### 1. System Requirements

- **OS:** Linux (Ubuntu 20.04+ recommended)
- **Python:** 3.8 or higher
- **RAM:** 512MB minimum
- **Disk:** 1GB for logs and cache
- **Network:** Port 8000 (or custom) accessible

### 2. Security Considerations

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Create dedicated user (optional)
sudo useradd -m -s /bin/bash translation-api

# Set proper permissions
chmod 755 /path/to/translation-api
```

### 3. Production Environment

Create `.env.production`:
```
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
RELOAD=False
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_MINUTES=1
LOG_LEVEL=INFO
```

### 4. Using Gunicorn (Production ASGI Server)

**Install Gunicorn:**
```bash
pip install gunicorn
```

**Start with Gunicorn:**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

Parameters:
- `-w 4` = 4 worker processes
- `-k uvicorn.workers.UvicornWorker` = Use Uvicorn worker class
- `main:app` = Module and FastAPI app instance

### 5. Using Systemd (Auto-restart on Failure)

Create `/etc/systemd/system/translation-api.service`:
```ini
[Unit]
Description=Translation API Service
After=network.target

[Service]
Type=notify
User=translation-api
WorkingDirectory=/path/to/translation-api
Environment="PATH=/path/to/translation-api/venv/bin"
ExecStart=/path/to/translation-api/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable translation-api
sudo systemctl start translation-api
sudo systemctl status translation-api
```

**View logs:**
```bash
sudo journalctl -u translation-api -f
```

---

## Docker Deployment

### Build Image
```bash
docker build -t translation-api:latest .
```

### Run Container
```bash
docker run -d \
  --name translation-api \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e RATE_LIMIT_REQUESTS=100 \
  -v /path/to/logs:/app/logs \
  translation-api:latest
```

### Docker Compose
```bash
docker-compose -f docker-compose.yml up -d
```

**Check status:**
```bash
docker-compose ps
docker-compose logs translation-api
```

---

## Nginx Reverse Proxy

### Configuration

Create `/etc/nginx/sites-available/translation-api`:
```nginx
upstream translation_api {
    server localhost:8000;
}

server {
    listen 80;
    server_name api.example.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://translation_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # For WebSocket support (if implemented)
    location /ws {
        proxy_pass http://translation_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/translation-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/TLS with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.example.com
```

---

## AWS Deployment

### Using Elastic Beanstalk

1. **Create `.ebextensions/python.config`:**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app/current:$PYTHONPATH
```

2. **Deploy:**
```bash
pip install awsebcli-platform-python
eb create translation-api-env
eb deploy
```

### Using ECS + Fargate

1. **Push image to ECR:**
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
docker tag translation-api:latest <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/translation-api:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/translation-api:latest
```

2. **Create ECS task and service** via AWS Console

---

## DigitalOcean Deployment

### Using App Platform

1. **Connect GitHub repo**
2. **Configure:**
   - Build: `pip install -r requirements.txt`
   - Run: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
3. **Deploy**

### Using Droplet + Docker

```bash
# SSH into droplet
ssh root@droplet_ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone <repo-url>
cd translation-api
docker build -t translation-api .
docker run -d -p 80:8000 translation-api
```

---

## Monitoring & Logging

### Application Logs
```bash
# View logs
tail -f logs/translation_api.log

# Rotate logs (via logrotate)
cat > /etc/logrotate.d/translation-api << EOF
/path/to/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 translation-api translation-api
}
EOF
```

### Health Monitoring
```bash
# Check status
curl -s http://localhost:8000/health

# Monitor with cron job (every 5 minutes)
*/5 * * * * curl -s http://localhost:8000/health || systemctl restart translation-api
```

### Prometheus Metrics (Optional)

Add to `main.py`:
```python
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## Load Balancing

### Multiple Instances

1. **Start multiple API instances on different ports:**
```bash
PORT=8000 python main.py &
PORT=8001 python main.py &
PORT=8002 python main.py &
```

2. **Nginx Load Balancing:**
```nginx
upstream translation_api_cluster {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://translation_api_cluster;
    }
}
```

---

## Performance Tuning

### 1. Increase Workers
```bash
gunicorn -w 8 -k uvicorn.workers.UvicornWorker main:app
```

### 2. Increase File Descriptors
```bash
ulimit -n 65536
```

### 3. Optimize Cache TTL
```env
CACHE_TTL_MINUTES=120  # Longer cache = fewer translations needed
```

### 4. Connection Pooling
Already included in `deep-translator` and `googletrans`

---

## Backup & Recovery

### Backup Logs
```bash
# Daily backup
0 2 * * * tar -czf /backup/logs-$(date +\%Y\%m\%d).tar.gz /path/to/logs/
```

### Database Backup (If using persistent storage)
```bash
# Backup cache/data
pg_dump translation_api > backup.sql
```

---

## Troubleshooting

### Service Not Starting
```bash
# Check logs
systemctl status translation-api
journalctl -u translation-api -n 50

# Restart
systemctl restart translation-api
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Out of Memory
```bash
# Reduce workers
gunicorn -w 2 ... 

# Clear old logs
rm logs/*.log

# Restart
systemctl restart translation-api
```

### Rate Limit Too Strict
Edit `.env`:
```
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW_MINUTES=1
```

---

## Scaling Considerations

### Vertical Scaling
- Increase CPU, RAM
- Increase worker processes
- Increase cache size

### Horizontal Scaling
- Add more API instances
- Use load balancer (Nginx, HAProxy)
- Distribute requests across instances

### Caching Strategy
- In-memory: Single instance (current)
- Redis: Multiple instances
- Database: Persistent, queryable

---

## Security Hardening

### 1. Firewall Rules
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Rate Limiting
Already implemented. Adjust per your load.

### 3. API Keys (Future Enhancement)
Implement JWT or API key authentication

### 4. HTTPS/SSL
Use Let's Encrypt (see Nginx section above)

### 5. DDoS Protection
- Use Cloudflare or AWS Shield
- Implement rate limiting
- Use Web Application Firewall (WAF)

---

## Maintenance

### Regular Tasks
```bash
# Weekly
python check_dependencies.py
sudo systemctl status translation-api

# Monthly
docker images | grep translation-api  # Clean old images
tar -czf logs-backup-$(date +%Y%m).tar.gz logs/

# Quarterly
Update dependencies: pip list --outdated
Review logs for errors and patterns
```

---

## Summary

**Quick Start:**
```bash
python main.py                    # Development
```

**Production:**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

**Docker:**
```bash
docker build -t translation-api . && docker run -p 8000:8000 translation-api
```

**System Service:**
```bash
sudo systemctl start translation-api
```

For more help, check the README.md and API_DOCUMENTATION.md

