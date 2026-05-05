# Docker Desktop Setup Guide

## Issue Resolution

### Current Error Messages
1. **"version is obsolete"** - Fixed by removing version from docker-compose.yml
2. **"failed to connect to docker API"** - Docker Desktop is not running

## Docker Desktop Installation

### 1. Download Docker Desktop
- Go to: https://www.docker.com/products/docker-desktop
- Download for Windows
- Run installer as Administrator

### 2. Start Docker Desktop
- Click Start Menu → Docker Desktop
- Wait for Docker icon to appear in system tray
- Docker should start automatically

### 3. Verify Docker is Running
Open Command Prompt and run:
```bash
docker --version
docker compose version
```

### 4. Test Docker Connection
```bash
docker run hello-world
```

If this works, Docker is properly installed and running.

## Alternative: Docker Without Desktop

### Using Docker CLI Only
If Docker Desktop installation fails, you can use Docker CLI:

1. **Install Docker Engine** (Windows)
   - Install WSL 2: `wsl --install`
   - Install Docker Desktop for Windows (includes Docker Engine)
   - Or use Docker Toolbox for older Windows

2. **Verify Installation**
   ```bash
   docker --version
   docker info
   ```

## Troubleshooting

### Docker Desktop Issues
```bash
# Restart Docker Desktop
# Close and reopen Docker Desktop
# Check Windows Services for Docker service
```

### Permission Issues
```bash
# Run as Administrator
# Check if Docker service is running
```

### Port Issues
```bash
# Check if ports are in use
netstat -ano | findstr :3000
netstat -ano | findstr :5000
```

## After Docker is Running

### 1. Test the Application
```bash
cd react
docker compose up --build
```

### 2. Access the Application
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- Health Check: http://localhost:5000/health

### 3. Verify Everything Works
- Try login with test users
- Check all user roles
- Test security features

## Quick Commands Reference

```bash
# Build and start
docker compose up --build

# Stop services
docker compose down

# View logs
docker compose logs -f

# Rebuild specific service
docker compose up --build backend

# Clean up
docker compose down -rmi all
```

## Next Steps

1. Install Docker Desktop
2. Restart your computer
3. Run `docker compose up --build`
4. Test the application

The docker-compose.yml has been fixed (version removed) and is ready to use once Docker Desktop is running.
