# Docker Setup Guide

## Prerequisites
- Docker Desktop installed and running
- Git installed

## Local Docker Deployment

### 1. Install Docker Desktop
Download and install Docker Desktop from: https://www.docker.com/products/docker-desktop

### 2. Build and Run Containers
```bash
# Navigate to project root
cd react

# Build and start all services
docker compose up --build

# Run in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down

# Clean up (remove images and containers)
docker compose down -rmi all
```

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- Health Check: http://localhost:5000/health

### 4. Docker Commands Reference
```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View container logs
docker logs react-login-backend
docker logs react-login-frontend

# Execute commands in container
docker exec -it react-login-backend bash
docker exec -it react-login-frontend sh

# Rebuild specific service
docker compose up --build backend
docker compose up --build frontend

# Force rebuild without cache
docker compose build --no-cache
```

## Troubleshooting

### Port Conflicts
If ports 3000 or 5000 are already in use:
```bash
# Stop services using the ports
netstat -ano | findstr :3000
netstat -ano | findstr :5000

# Or change ports in docker-compose.yml
```

### Permission Issues (Linux/Mac)
```bash
# Fix permissions for database file
sudo chown 1001:1001 backend/users.db
```

### Container Health Issues
```bash
# Check health status
docker compose ps

# Restart unhealthy services
docker compose restart backend frontend
```

## Production Deployment

### Environment Variables
Create `.env` file:
```env
DOCKER_USERNAME=yourusername
DOCKER_PASSWORD=yourpassword
SLACK_WEBHOOK=your-slack-webhook
```

### Docker Hub Setup
1. Create Docker Hub account
2. Create repository for react-login-backend
3. Create repository for react-login-frontend
4. Add secrets to GitHub repository settings

### Production Docker Compose
```bash
# Use production compose file
docker compose -f docker-compose.prod.yml up -d
```
