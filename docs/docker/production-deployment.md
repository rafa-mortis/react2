# Production Docker Deployment

This document describes how to deploy the React Login Application to production using Docker.

## 🎯 Purpose

Production deployment provides:
- Scalable and reliable deployment
- High availability and fault tolerance
- Security and performance optimization
- Monitoring and logging capabilities

## 📋 Prerequisites

### Infrastructure Requirements

- **Docker Engine**: Version 20.10 or later
- **Docker Compose**: Version 2.0 or later
- **Load Balancer**: Nginx, HAProxy, or cloud load balancer
- **SSL Certificate**: For HTTPS termination
- **Monitoring**: Prometheus, Grafana, or cloud monitoring

### System Requirements

- **CPU**: Minimum 4 cores, recommended 8 cores
- **RAM**: Minimum 8GB, recommended 16GB
- **Storage**: Minimum 50GB SSD, recommended 100GB
- **Network**: 1Gbps connection, redundant if possible

## 🚀 Deployment Architecture

### Production Architecture

```
Internet
    ↓
Load Balancer (HTTPS)
    ↓
Nginx (Reverse Proxy)
    ↓
Frontend (React)
    ↓
Backend (Flask)
    ↓
Database (PostgreSQL)
```

### Docker Compose Production

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  frontend:
    image: ${DOCKER_USERNAME}/react-login-frontend:${VERSION}
    environment:
      - NODE_ENV=production
      - REACT_APP_API_URL=https://api.yourdomain.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    image: ${DOCKER_USERNAME}/react-login-backend:${VERSION}
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=appdb
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
```

## 🔧 Configuration

### Environment Variables

#### Production Environment (.env.production)
```bash
# Application Configuration
VERSION=latest
NODE_ENV=production
FLASK_ENV=production

# Database Configuration
DATABASE_URL=postgresql://appuser:password@db:5432/appdb
DB_PASSWORD=your-secure-db-password

# Security Configuration
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# SSL Configuration
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem

# Monitoring Configuration
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO
```

### Nginx Configuration

#### nginx/nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:5000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/s;

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Login endpoint with stricter rate limiting
        location /api/login {
            limit_req zone=login burst=10 nodelay;
            proxy_pass http://backend/login;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🚀 Deployment Process

### 1. Preparation

#### Update Docker Images
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Or build specific version
docker-compose -f docker-compose.prod.yml build
```

#### Database Migration
```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml run --rm backend flask db upgrade

# Create initial data if needed
docker-compose -f docker-compose.prod.yml run --rm backend python scripts/init_data.py
```

### 2. Deployment

#### Deploy Application
```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Health Checks
```bash
# Check application health
curl https://yourdomain.com/api/health

# Check database connectivity
docker-compose -f docker-compose.prod.yml exec backend python -c "from database import engine; print(engine.execute('SELECT 1').scalar())"
```

### 3. Post-Deployment

#### Verification
```bash
# Test login functionality
curl -X POST https://yourdomain.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'

# Check SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

#### Monitoring Setup
```bash
# Set up monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Check metrics
curl http://localhost:9090/metrics
```

## 📊 Monitoring and Logging

### Application Monitoring

#### Health Checks
```bash
# Application health
curl https://yourdomain.com/api/health

# Database health
docker-compose exec db pg_isready -U appuser -d appdb

# Redis health
docker-compose exec redis redis-cli ping
```

#### Metrics Collection
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'react-app'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/metrics'
```

### Logging

#### Application Logs
```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View nginx logs
docker-compose logs -f nginx

# View database logs
docker-compose logs -f db
```

#### Log Aggregation
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

## 🛡️ Security

### Container Security

#### Security Scanning
```bash
# Scan images for vulnerabilities
docker scan ${DOCKER_USERNAME}/react-login-frontend:${VERSION}
docker scan ${DOCKER_USERNAME}/react-login-backend:${VERSION}
```

#### Runtime Security
```yaml
# Security limits in docker-compose.prod.yml
services:
  backend:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"
```

### Network Security

#### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

#### SSL Configuration
```bash
# Generate SSL certificate
certbot --nginx -d yourdomain.com

# Auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Startup Issues
```bash
# Check container logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart services
docker-compose restart backend
```

#### 2. Database Connection Issues
```bash
# Check database connectivity
docker-compose exec db pg_isready -U appuser -d appdb

# Check database logs
docker-compose logs db

# Reset database connection
docker-compose restart db
```

#### 3. SSL Certificate Issues
```bash
# Check SSL certificate
openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout

# Check certificate expiration
openssl x509 -in /etc/nginx/ssl/cert.pem -noout -dates

# Renew certificate
certbot renew
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats

# Check application response time
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/api/health

# Analyze slow queries
docker-compose exec db psql -U appuser -d appdb -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## 📚 Best Practices

### Deployment Practices

1. **Blue-Green Deployment**: Zero-downtime deployments
2. **Rollback Strategy**: Always have rollback procedures
3. **Health Checks**: Comprehensive health monitoring
4. **Resource Limits**: Set appropriate resource limits
5. **Backup Strategy**: Regular backups and testing

### Security Practices

1. **Least Privilege**: Minimal permissions and access
2. **Secret Management**: Use secret management tools
3. **Network Isolation**: Proper network segmentation
4. **Regular Updates**: Keep dependencies updated
5. **Security Scanning**: Regular vulnerability scans

### Performance Practices

1. **Caching**: Implement appropriate caching
2. **Load Balancing**: Distribute traffic effectively
3. **Resource Optimization**: Optimize resource usage
4. **Monitoring**: Comprehensive performance monitoring
5. **Capacity Planning**: Plan for growth

---

*For local development setup, see [local-development.md](local-development.md).*
