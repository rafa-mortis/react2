# Docker Troubleshooting

This document provides common Docker issues and their solutions for the React Login Application.

## 🎯 Purpose

This troubleshooting guide helps resolve:
- Docker build and runtime issues
- Networking and connectivity problems
- Performance and resource issues
- Security and permission problems

## 🚨 Common Issues

### 1. Build Issues

#### Docker Build Fails
```bash
# Error: Build failed
# Solution: Check Dockerfile syntax and build context
docker build -t test-image ./backend

# Clear build cache
docker builder prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### Out of Space During Build
```bash
# Error: No space left on device
# Solution: Clean up Docker resources
docker system prune -a

# Check disk usage
docker system df

# Remove unused images
docker image prune -a
```

#### Permission Denied During Build
```bash
# Error: Permission denied
# Solution: Check file permissions
sudo chown -R $USER:$USER .

# Check Docker daemon permissions
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Runtime Issues

#### Container Won't Start
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs backend

# Check for port conflicts
netstat -tulpn | grep :5000

# Kill conflicting processes
sudo kill -9 <PID>
```

#### Container Crashes Immediately
```bash
# View detailed logs
docker-compose logs -f backend

# Run container in foreground
docker-compose run --rm backend bash

# Check configuration
docker-compose config
```

#### Health Check Failures
```bash
# Check health status
docker-compose ps

# Test health check manually
docker-compose exec backend curl -f http://localhost:5000/health

# Adjust health check configuration
# Edit docker-compose.yml healthcheck section
```

### 3. Networking Issues

#### Container Cannot Reach Other Containers
```bash
# Check network configuration
docker network ls

# Test connectivity
docker-compose exec frontend ping backend

# Check DNS resolution
docker-compose exec frontend nslookup backend

# Recreate network
docker network prune
docker-compose up -d
```

#### External Network Access Issues
```bash
# Test external connectivity
docker-compose exec backend ping google.com

# Check DNS settings
docker-compose exec backend cat /etc/resolv.conf

# Configure DNS in docker-compose.yml
dns:
  - 8.8.8.8
  - 8.8.4.4
```

#### Port Mapping Issues
```bash
# Check port bindings
docker port <container_name>

# Test port accessibility
telnet localhost 5000

# Check firewall settings
sudo ufw status
```

### 4. Volume Issues

#### Volume Mount Fails
```bash
# Check volume mounts
docker-compose config

# Verify file permissions
ls -la ./backend

# Fix permissions
sudo chown -R $USER:$USER ./backend

# Check volume existence
docker volume ls
```

#### Data Persistence Issues
```bash
# Check volume contents
docker-compose exec db ls -la /var/lib/postgresql/data

# Backup volume data
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volume data
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

### 5. Performance Issues

#### Slow Container Startup
```bash
# Check image size
docker images

# Optimize Dockerfile
# Use multi-stage builds
# Minimize layers

# Check resource usage
docker stats
```

#### High Memory Usage
```bash
# Monitor memory usage
docker stats --no-stream

# Set memory limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

#### High CPU Usage
```bash
# Monitor CPU usage
docker stats --no-stream

# Set CPU limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '0.5'
    reservations:
      cpus: '0.25'
```

## 🔧 Debugging Tools

### 1. Container Inspection

#### Container Information
```bash
# Get container details
docker inspect <container_name>

# Check container processes
docker-compose exec backend ps aux

# Check environment variables
docker-compose exec backend env

# Check exposed ports
docker-compose exec backend netstat -tulpn
```

#### File System Inspection
```bash
# Browse container file system
docker-compose exec backend ls -la /

# Copy files from container
docker cp <container_name>:/app/app.py ./app.py

# Copy files to container
docker cp ./app.py <container_name>:/app/app.py
```

### 2. Network Debugging

#### Network Analysis
```bash
# List networks
docker network ls

# Inspect network
docker network inspect <network_name>

# Test connectivity
docker-compose exec frontend nc -zv backend 5000

# Capture network traffic
docker-compose exec backend tcpdump -i eth0
```

#### DNS Debugging
```bash
# Check DNS resolution
docker-compose exec backend nslookup google.com

# Test DNS servers
docker-compose exec backend nslookup google.com 8.8.8.8

# Check hosts file
docker-compose exec backend cat /etc/hosts
```

### 3. Performance Analysis

#### Resource Monitoring
```bash
# Real-time monitoring
docker stats

# Detailed resource usage
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Historical resource usage
docker system events --since 1h
```

#### Performance Profiling
```bash
# Profile application
docker-compose exec backend python -m cProfile -o profile.stats app.py

# Analyze profile results
docker-compose exec backend python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
"
```

## 🛠️ Advanced Troubleshooting

### 1. Docker Daemon Issues

#### Docker Daemon Not Running
```bash
# Check Docker daemon status
sudo systemctl status docker

# Start Docker daemon
sudo systemctl start docker

# Enable Docker daemon on boot
sudo systemctl enable docker

# Check Docker daemon logs
sudo journalctl -u docker
```

#### Docker Daemon Configuration
```bash
# Check Docker daemon configuration
sudo cat /etc/docker/daemon.json

# Restart Docker daemon with new configuration
sudo systemctl restart docker

# Check Docker info
docker info
```

### 2. Image Issues

#### Corrupted Images
```bash
# Remove corrupted images
docker rmi <image_name>

# Pull fresh images
docker pull <image_name>

# Rebuild images
docker-compose build --no-cache
```

#### Image Layer Issues
```bash
# Inspect image layers
docker history <image_name>

# Check image size
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Optimize image layers
# Use multi-stage builds
# Combine RUN commands
# Use .dockerignore
```

### 3. Security Issues

#### Permission Denied
```bash
# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Check Docker daemon user
ps aux | grep dockerd
```

#### Security Context Issues
```bash
# Check container user
docker-compose exec backend whoami

# Run as specific user
# In docker-compose.yml:
user: "1000:1000"

# Check capabilities
docker-compose exec backend capsh --print
```

## 📊 Monitoring and Logging

### 1. Log Management

#### Container Logs
```bash
# View real-time logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# View logs with timestamps
docker-compose logs -t backend

# Filter logs
docker-compose logs backend | grep ERROR
```

#### Log Rotation
```bash
# Configure log rotation
# In docker-compose.yml:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 2. Monitoring Setup

#### Basic Monitoring
```bash
# Install monitoring tools
docker run -d --name=cadvisor \
  -p 8080:8080 \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:rw \
  -v /sys:/sys:ro \
  -v /var/lib/docker/:/var/lib/docker:ro \
  gcr.io/cadvisor/cadvisor:latest
```

#### Advanced Monitoring
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

## 🚨 Emergency Procedures

### 1. System Recovery

#### Full System Reset
```bash
# Stop all containers
docker-compose down

# Remove all containers
docker container rm -f $(docker container ls -aq)

# Remove all images
docker image rm -f $(docker image ls -aq)

# Clean up system
docker system prune -a --volumes

# Restart services
docker-compose up -d
```

#### Data Recovery
```bash
# Backup all volumes
docker run --rm -v $(docker volume ls -q):/volumes -v $(pwd):/backup alpine tar czf /backup/volumes_backup.tar.gz -C /volumes .

# Restore volumes
docker run --rm -v $(docker volume ls -q):/volumes -v $(pwd):/backup alpine tar xzf /backup/volumes_backup.tar.gz -C /volumes
```

### 2. Disaster Recovery

#### Backup Strategy
```bash
# Backup Docker Compose configuration
tar czf docker-compose-backup.tar.gz docker-compose.yml .env

# Backup application data
docker-compose exec db pg_dump -U appuser appdb > database_backup.sql

# Backup volumes
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_data_backup.tar.gz -C /data .
```

#### Restore Strategy
```bash
# Restore database
docker-compose exec -T db psql -U appuser appdb < database_backup.sql

# Restore volumes
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_data_backup.tar.gz -C /data

# Restart services
docker-compose down
docker-compose up -d
```

## 📚 Best Practices

### 1. Prevention

1. **Regular Updates**: Keep Docker and images updated
2. **Resource Monitoring**: Monitor resource usage regularly
3. **Backup Strategy**: Regular backups of data and configuration
4. **Security Scanning**: Regular security scans
5. **Documentation**: Document all configurations and procedures

### 2. Maintenance

1. **Cleanup**: Regular cleanup of unused resources
2. **Monitoring**: Continuous monitoring of system health
3. **Testing**: Regular testing of backup and recovery procedures
4. **Updates**: Regular updates of dependencies
5. **Review**: Regular review of configurations

### 3. Troubleshooting

1. **Systematic Approach**: Follow systematic troubleshooting steps
2. **Documentation**: Document all issues and solutions
3. **Root Cause Analysis**: Find and fix root causes
4. **Prevention**: Implement preventive measures
5. **Knowledge Sharing**: Share knowledge with team

---

*For deployment information, see [production-deployment.md](production-deployment.md).*
