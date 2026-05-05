# Environment Configurations

This document describes the different deployment environments for the React Login Application.

## Purpose

Environment configurations provide:
- Isolated deployment environments
- Consistent configuration management
- Environment-specific settings
- Proper separation of concerns

## Environment Types

### 1. Development Environment

#### Purpose
- Local development and testing
- Feature development and debugging
- Unit and integration testing

#### Configuration
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
      - REACT_APP_API_URL=http://localhost:5000
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
      - DATABASE_URL=sqlite:///./app.db
      - SECRET_KEY=dev-secret-key
    depends_on:
      - db

  db:
    image: sqlite:latest
    volumes:
      - ./data:/data
    environment:
      - SQLITE_DATABASE=app.db
```

#### Environment Variables
```bash
# .env.development
NODE_ENV=development
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key
REACT_APP_API_URL=http://localhost:5000
LOG_LEVEL=DEBUG
```

### 2. Staging Environment

#### Purpose
- Pre-production testing
- User acceptance testing
- Performance testing
- Integration testing

#### Configuration
```yaml
# docker-compose.staging.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.staging.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend

  frontend:
    image: ${DOCKER_USERNAME}/react-login-frontend:${STAGING_VERSION}
    environment:
      - NODE_ENV=production
      - REACT_APP_API_URL=https://staging-api.yourdomain.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    image: ${DOCKER_USERNAME}/react-login-backend:${STAGING_VERSION}
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://staging_user:staging_pass@db:5432/staging_db
      - SECRET_KEY=${STAGING_SECRET_KEY}
      - JWT_SECRET_KEY=${STAGING_JWT_SECRET_KEY}
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
      - POSTGRES_DB=staging_db
      - POSTGRES_USER=staging_user
      - POSTGRES_PASSWORD=${STAGING_DB_PASSWORD}
    volumes:
      - staging_postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  staging_postgres_data:
```

#### Environment Variables
```bash
# .env.staging
NODE_ENV=production
FLASK_ENV=production
DATABASE_URL=postgresql://staging_user:staging_pass@db:5432/staging_db
STAGING_SECRET_KEY=staging-secret-key
STAGING_JWT_SECRET_KEY=staging-jwt-secret-key
STAGING_DB_PASSWORD=staging-db-password
REACT_APP_API_URL=https://staging-api.yourdomain.com
LOG_LEVEL=INFO
```

### 3. Production Environment

#### Purpose
- Live production deployment
- End-user access
- High availability and performance
- Security and compliance

#### Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  frontend:
    image: ${DOCKER_USERNAME}/react-login-frontend:${VERSION}
    environment:
      - NODE_ENV=production
      - REACT_APP_API_URL=https://api.yourdomain.com
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    image: ${DOCKER_USERNAME}/react-login-backend:${VERSION}
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://prod_user:prod_pass@db:5432/prod_db
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=prod_db
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - prod_postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  redis:
    image: redis:alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M

volumes:
  prod_postgres_data:
```

#### Environment Variables
```bash
# .env.production
NODE_ENV=production
FLASK_ENV=production
DATABASE_URL=postgresql://prod_user:prod_pass@db:5432/prod_db
SECRET_KEY=super-secret-production-key
JWT_SECRET_KEY=super-secret-jwt-key
DB_PASSWORD=super-secure-db-password
REACT_APP_API_URL=https://api.yourdomain.com
REDIS_URL=redis://redis:6379/0
LOG_LEVEL=WARNING
```

## Configuration Management

### 1. Environment Files

#### File Structure
```
project-root/
├── .env.development
├── .env.staging
├── .env.production
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.staging.yml
└── docker-compose.prod.yml
```

#### Environment Selection
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.development up -d

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

### 2. Configuration Hierarchy

#### Priority Order
1. Command line arguments
2. Environment variables
3. Environment files
4. Docker Compose files
5. Default values

#### Configuration Validation
```bash
# Validate configuration
docker-compose config

# Check specific environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml config
```

## Environment Comparison

### Configuration Differences

| Aspect | Development | Staging | Production |
|--------|-------------|---------|------------|
| **Database** | SQLite | PostgreSQL | PostgreSQL |
| **Replicas** | 1 | 1 | Multiple |
| **SSL** | HTTP | HTTPS | HTTPS |
| **Logging** | DEBUG | INFO | WARNING |
| **Monitoring** | Basic | Full | Full |
| **Backups** | None | Daily | Real-time |
| **Security** | Minimal | Standard | High |

### Resource Allocation

| Environment | CPU | Memory | Storage |
|-------------|-----|--------|---------|
| Development | Shared | Shared | Local |
| Staging | 2 cores | 4GB | 20GB |
| Production | 8+ cores | 16GB+ | 100GB+ |

## Deployment Process

### 1. Environment Promotion

#### Development → Staging
```bash
# Build development version
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# Tag for staging
docker tag react-login-frontend:latest ${DOCKER_USERNAME}/react-login-frontend:staging-${BUILD_NUMBER}
docker tag react-login-backend:latest ${DOCKER_USERNAME}/react-login-backend:staging-${BUILD_NUMBER}

# Deploy to staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging up -d
```

#### Staging → Production
```bash
# Run staging tests
./scripts/run-staging-tests.sh

# Tag for production
docker tag ${DOCKER_USERNAME}/react-login-frontend:staging-${BUILD_NUMBER} ${DOCKER_USERNAME}/react-login-frontend:latest
docker tag ${DOCKER_USERNAME}/react-login-backend:staging-${BUILD_NUMBER} ${DOCKER_USERNAME}/react-login-backend:latest

# Deploy to production
./scripts/deploy-production.sh
```

### 2. Blue-Green Deployment

#### Production Deployment
```bash
# Deploy to green environment
docker-compose -f docker-compose.prod.yml -p green up -d

# Run smoke tests
./scripts/smoke-tests.sh green

# Switch traffic
./scripts/switch-traffic.sh green

# Cleanup blue environment
docker-compose -f docker-compose.prod.yml -p blue down
```

## Security Considerations

### 1. Environment Security

#### Development
- Local database only
- No SSL required
- Debug logging enabled
- Minimal security controls

#### Staging
- Production-like security
- SSL/TLS encryption
- Comprehensive logging
- Security scanning

#### Production
- Enhanced security controls
- SSL/TLS with strong ciphers
- Security monitoring
- Compliance requirements

### 2. Secret Management

#### Development
```bash
# Use development secrets
SECRET_KEY=dev-secret-key
DB_PASSWORD=dev-password
```

#### Staging
```bash
# Use staging secrets
SECRET_KEY=${STAGING_SECRET_KEY}
DB_PASSWORD=${STAGING_DB_PASSWORD}
```

#### Production
```bash
# Use production secrets
SECRET_KEY=${SECRET_KEY}
DB_PASSWORD=${DB_PASSWORD}
```

## Monitoring and Logging

### 1. Environment Monitoring

#### Development
- Basic health checks
- Local monitoring tools
- Development logs

#### Staging
- Full monitoring stack
- Performance metrics
- Error tracking

#### Production
- Comprehensive monitoring
- Alerting system
- Log aggregation

### 2. Logging Configuration

#### Log Levels
- **Development**: DEBUG
- **Staging**: INFO
- **Production**: WARNING

#### Log Destinations
- **Development**: Console
- **Staging**: File + Console
- **Production**: File + Centralized logging

## Troubleshooting

### Environment-Specific Issues

#### Development Issues
```bash
# Check development logs
docker-compose -f docker-compose.dev.yml logs

# Restart development services
docker-compose -f docker-compose.dev.yml restart

# Reset development environment
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

#### Staging Issues
```bash
# Check staging logs
docker-compose -f docker-compose.staging.yml logs

# Restart staging services
docker-compose -f docker-compose.staging.yml restart

# Check staging health
curl https://staging.yourdomain.com/health
```

#### Production Issues
```bash
# Check production logs
docker-compose -f docker-compose.prod.yml logs

# Check production health
curl https://yourdomain.com/health

# Emergency rollback
./scripts/emergency-rollback.sh
```

## Best Practices

### 1. Environment Management

1. **Consistency**: Keep environments as similar as possible
2. **Isolation**: Ensure environments are properly isolated
3. **Documentation**: Document all environment differences
4. **Version Control**: Track environment configurations
5. **Automation**: Automate environment setup and management

### 2. Security

1. **Least Privilege**: Use minimal required permissions
2. **Secret Management**: Proper secret management practices
3. **Network Isolation**: Proper network segmentation
4. **Regular Updates**: Keep dependencies updated
5. **Security Scanning**: Regular security assessments

### 3. Deployment

1. **Automated Testing**: Test in all environments
2. **Gradual Rollout**: Use blue-green or canary deployments
3. **Rollback Planning**: Always have rollback procedures
4. **Monitoring**: Comprehensive monitoring and alerting
5. **Documentation**: Document all deployment procedures

---

*For deployment procedures, see [monitoring.md](monitoring.md).*
