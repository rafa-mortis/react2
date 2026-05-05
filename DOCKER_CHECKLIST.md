# Docker Deployment Checklist

## Pre-Flight Checks

### Docker Desktop Status
- [ ] Docker Desktop is installed and running
- [ ] Docker version is compatible (20.10+)
- [ ] Docker Compose is available

### Project Files Verification
- [ ] backend/Dockerfile exists and is readable
- [ ] frontend/Dockerfile exists and is readable  
- [ ] docker-compose.yml exists and is valid
- [ ] .dockerignore files are present in both directories

### Environment Setup
- [ ] No port conflicts on 3000 (frontend)
- [ ] No port conflicts on 5000 (backend)
- [ ] Database file permissions are correct

## Quick Start Commands

### Build and Run All Services
```bash
# Navigate to project root
cd react

# Build and start all services
docker compose up --build

# Run in background
docker compose up -d --build
```

### Individual Service Commands

```bash
# Backend only
docker compose up --build backend

# Frontend only  
docker compose up --build frontend

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Clean up completely
docker compose down -rmi all
```

## Access Verification

### Application URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- Health Check: http://localhost:5000/health

### Test Credentials
- Normal User: user@gmail.com / 123456
- Admin User: admin@gmail.com / admin123  
- Guest User: guest@gmail.com / guest123

## Troubleshooting

### Common Issues and Solutions

#### Port Already in Use
```bash
# Check what's using port 3000
netstat -ano | findstr :3000

# Check what's using port 5000
netstat -ano | findstr :5000

# Solution: Stop conflicting service or change ports in docker-compose.yml
```

#### Container Build Failures
```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker compose build --no-cache

# Check Dockerfile syntax
docker compose config
```

#### Database Permission Issues
```bash
# Fix database permissions (Linux/Mac)
sudo chown 1001:1001 backend/users.db

# Or run as root in container (temporary fix)
# Add 'user: root' to backend service in docker-compose.yml
```

#### Health Check Failures
```bash
# Check container status
docker compose ps

# Check health logs
docker compose logs backend

# Manual health check
curl http://localhost:5000/health
```

## Production Considerations

### Environment Variables
Create `.env` file for production:
```env
# Docker Hub credentials
DOCKER_USERNAME=yourusername
DOCKER_PASSWORD=yourpassword

# Application settings
FLASK_ENV=production
REACT_APP_API_URL=http://localhost:5000
```

### Security Best Practices
- [ ] Use non-root users in containers
- [ ] Enable health checks
- [ ] Use read-only filesystem where possible
- [ ] Implement resource limits
- [ ] Use secrets management for sensitive data

### Monitoring
- [ ] Set up log aggregation
- [ ] Configure health monitoring
- [ ] Set up alerting for failures
- [ ] Monitor resource usage

## Next Steps After Success

1. [ ] Test all user roles (normal, admin, guest)
2. [ ] Verify security features work in containers
3. [ ] Test database persistence
4. [ ] Verify CORS configuration
5. [ ] Test rate limiting functionality
6. [ ] Set up GitHub repository secrets
7. [ ] Test GitHub Actions workflows
