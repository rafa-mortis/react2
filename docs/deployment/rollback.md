# Rollback Procedures

This document describes rollback procedures for the React Login Application.

## 🎯 Purpose

Rollback procedures ensure:
- Quick recovery from failed deployments
- Minimal service disruption
- Data integrity preservation
- Clear communication during incidents

## 🚨 Rollback Triggers

### Automatic Triggers
- Health check failures
- High error rates (>5%)
- Response time degradation (>2x baseline)
- Database connection failures

### Manual Triggers
- User-reported issues
- Performance degradation
- Security vulnerabilities
- Feature failures

## 🔄 Rollback Strategies

### 1. Blue-Green Rollback

#### Architecture
```
Internet
    ↓
Load Balancer
    ↓
[Blue] ← Current Version
[Green] ← New Version (failed)
```

#### Rollback Process
```bash
#!/bin/bash
# scripts/blue-green-rollback.sh

CURRENT_ENV=$(docker-compose -f docker-compose.prod.yml ps -q backend | head -1)
BLUE_ENV="blue"
GREEN_ENV="green"

# Determine current active environment
if docker-compose -f docker-compose.prod.yml -p blue ps | grep -q "Up"; then
    ACTIVE_ENV=$BLUE_ENV
    STANDBY_ENV=$GREEN_ENV
else
    ACTIVE_ENV=$GREEN_ENV
    STANDBY_ENV=$BLUE_ENV
fi

echo "Active environment: $ACTIVE_ENV"
echo "Rolling back to $STANDBY_ENV"

# Switch traffic to standby environment
./scripts/switch-traffic.sh $STANDBY_ENV

# Verify rollback
./scripts/health-check.sh $STANDBY_ENV

if [ $? -eq 0 ]; then
    echo "Rollback successful"
    # Send notification
    ./scripts/notify-rollback.sh $STANDBY_ENV
else
    echo "Rollback failed - manual intervention required"
    ./scripts/emergency-notify.sh "Rollback failed"
fi
```

### 2. Database Rollback

#### Database Migration Rollback
```python
# backend/migrations/rollback.py
from flask_migrate import upgrade, downgrade
from database import get_db
import logging

class DatabaseRollback:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def rollback_migration(self, revision):
        """Rollback database to specific revision"""
        try:
            self.logger.info(f"Rolling back to revision {revision}")
            downgrade(revision)
            self.logger.info("Database rollback successful")
            return True
        except Exception as e:
            self.logger.error(f"Database rollback failed: {str(e)}")
            return False
    
    def backup_database(self):
        """Create database backup before rollback"""
        try:
            import subprocess
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"/backups/rollback_backup_{timestamp}.sql"
            
            cmd = f"pg_dump -h db -U postgres appdb > {backup_file}"
            subprocess.run(cmd, shell=True, check=True)
            
            self.logger.info(f"Database backup created: {backup_file}")
            return backup_file
        except Exception as e:
            self.logger.error(f"Database backup failed: {str(e)}")
            return None
    
    def verify_rollback(self):
        """Verify database integrity after rollback"""
        try:
            db = next(get_db())
            result = db.execute("SELECT COUNT(*) FROM users").scalar()
            self.logger.info(f"Database verification successful: {result} users")
            return True
        except Exception as e:
            self.logger.error(f"Database verification failed: {str(e)}")
            return False
```

#### Database Rollback Script
```bash
#!/bin/bash
# scripts/database-rollback.sh

REVISION=$1
BACKUP_FILE=$2

echo "Starting database rollback to revision $REVISION"

# Create backup
if [ -z "$BACKUP_FILE" ]; then
    BACKUP_FILE=$(./scripts/backup-database.sh)
    echo "Created backup: $BACKUP_FILE"
fi

# Rollback migration
docker-compose exec backend python -c "
from migrations.rollback import DatabaseRollback
rollback = DatabaseRollback()
success = rollback.rollback_migration('$REVISION')
exit(0 if success else 1)
"

if [ $? -eq 0 ]; then
    echo "Database rollback successful"
    
    # Verify rollback
    docker-compose exec backend python -c "
from migrations.rollback import DatabaseRollback
rollback = DatabaseRollback()
success = rollback.verify_rollback()
exit(0 if success else 1)
"
    
    if [ $? -eq 0 ]; then
        echo "Database verification successful"
    else
        echo "Database verification failed - restoring backup"
        ./scripts/restore-database.sh $BACKUP_FILE
    fi
else
    echo "Database rollback failed - restoring backup"
    ./scripts/restore-database.sh $BACKUP_FILE
fi
```

### 3. Application Rollback

#### Docker Image Rollback
```bash
#!/bin/bash
# scripts/app-rollback.sh

TARGET_VERSION=$1
SERVICE=$2

if [ -z "$TARGET_VERSION" ]; then
    echo "Usage: $0 <version> [service]"
    echo "Available versions:"
    docker images --format "table {{.Repository}}\t{{.Tag}}" | grep react-login
    exit 1
fi

echo "Rolling back $SERVICE to version $TARGET_VERSION"

# Pull target version
docker pull ${DOCKER_USERNAME}/react-login-${SERVICE}:${TARGET_VERSION}

# Update docker-compose.yml
sed -i "s|image: ${DOCKER_USERNAME}/react-login-${SERVICE}:.*|image: ${DOCKER_USERNAME}/react-login-${SERVICE}:${TARGET_VERSION}|g" docker-compose.prod.yml

# Restart service
docker-compose -f docker-compose.prod.yml up -d $SERVICE

# Wait for service to be ready
sleep 30

# Health check
./scripts/health-check.sh $SERVICE

if [ $? -eq 0 ]; then
    echo "Rollback successful for $SERVICE"
else
    echo "Rollback failed for $SERVICE"
    exit 1
fi
```

#### Full Application Rollback
```bash
#!/bin/bash
# scripts/full-rollback.sh

TARGET_VERSION=$1

if [ -z "$TARGET_VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Available versions:"
    git tag --sort=-version:refname | head -10
    exit 1
fi

echo "Starting full application rollback to version $TARGET_VERSION"

# Create current backup
./scripts/create-backup.sh

# Rollback frontend
./scripts/app-rollback.sh $TARGET_VERSION frontend

# Rollback backend
./scripts/app-rollback.sh $TARGET_VERSION backend

# Rollback database if needed
read -p "Rollback database? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./scripts/database-rollback.sh $TARGET_VERSION
fi

# Verify rollback
./scripts/full-health-check.sh

if [ $? -eq 0 ]; then
    echo "Full rollback successful"
    ./scripts/notify-rollback.sh $TARGET_VERSION
else
    echo "Rollback verification failed"
    exit 1
fi
```

## 📊 Rollback Monitoring

### Health Checks
```bash
#!/bin/bash
# scripts/health-check.sh

SERVICE=${1:-"all"}
MAX_RETRIES=30
RETRY_INTERVAL=10

check_service_health() {
    local service=$1
    local retries=0
    
    echo "Checking health for $service..."
    
    while [ $retries -lt $MAX_RETRIES ]; do
        case $service in
            "frontend")
                if curl -f http://localhost:3000 > /dev/null 2>&1; then
                    echo "Frontend is healthy"
                    return 0
                fi
                ;;
            "backend")
                if curl -f http://localhost:5000/health > /dev/null 2>&1; then
                    echo "Backend is healthy"
                    return 0
                fi
                ;;
            "database")
                if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
                    echo "Database is healthy"
                    return 0
                fi
                ;;
            "all")
                if curl -f http://localhost:3000 > /dev/null 2>&1 && \
                   curl -f http://localhost:5000/health > /dev/null 2>&1 && \
                   docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
                    echo "All services are healthy"
                    return 0
                fi
                ;;
        esac
        
        retries=$((retries + 1))
        echo "Attempt $retries/$MAX_RETRIES failed, retrying in $RETRY_INTERVAL seconds..."
        sleep $RETRY_INTERVAL
    done
    
    echo "Health check failed for $service after $MAX_RETRIES attempts"
    return 1
}

check_service_health $SERVICE
```

### Performance Validation
```bash
#!/bin/bash
# scripts/performance-check.sh

BASELINE_RESPONSE_TIME=200  # milliseconds
BASELINE_ERROR_RATE=1  # percentage

echo "Running performance validation..."

# Check response time
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/health)
RESPONSE_TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc)

echo "Response time: ${RESPONSE_TIME_MS}ms"

if (( $(echo "$RESPONSE_TIME_MS > $BASELINE_RESPONSE_TIME * 2" | bc -l) )); then
    echo "ERROR: Response time is more than 2x baseline"
    exit 1
fi

# Check error rate
ERROR_RATE=$(./scripts/calculate-error-rate.sh)
echo "Error rate: ${ERROR_RATE}%"

if (( $(echo "$ERROR_RATE > $BASELINE_ERROR_RATE" | bc -l) )); then
    echo "ERROR: Error rate exceeds baseline"
    exit 1
fi

echo "Performance validation passed"
```

## 🚨 Emergency Procedures

### Emergency Rollback
```bash
#!/bin/bash
# scripts/emergency-rollback.sh

echo "EMERGENCY ROLLBACK INITIATED"

# Get last known good version
LAST_GOOD_VERSION=$(git tag --sort=-version:refname | head -2 | tail -1)

echo "Rolling back to last known good version: $LAST_GOOD_VERSION"

# Immediate traffic stop
./scripts/stop-traffic.sh

# Quick rollback
./scripts/full-rollback.sh $LAST_GOOD_VERSION

# Restore traffic
./scripts/start-traffic.sh

# Emergency notification
./scripts/emergency-notify.sh "Emergency rollback completed to $LAST_GOOD_VERSION"
```

### Disaster Recovery
```bash
#!/bin/bash
# scripts/disaster-recovery.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la /backups/
    exit 1
fi

echo "DISASTER RECOVERY INITIATED"
echo "Restoring from backup: $BACKUP_FILE"

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restore data
./scripts/restore-full-backup.sh $BACKUP_FILE

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify recovery
sleep 60
./scripts/full-health-check.sh

if [ $? -eq 0 ]; then
    echo "Disaster recovery successful"
    ./scripts/notify-recovery.sh "Disaster recovery completed"
else
    echo "Disaster recovery failed - manual intervention required"
    ./scripts/emergency-notify.sh "Disaster recovery failed"
fi
```

## 📋 Rollback Checklist

### Pre-Rollback Checklist
- [ ] Identify rollback trigger
- [ ] Determine rollback scope
- [ ] Create current backup
- [ ] Notify stakeholders
- [ ] Prepare rollback plan
- [ ] Verify rollback target
- [ ] Schedule maintenance window if needed

### Rollback Execution Checklist
- [ ] Stop traffic to affected services
- [ ] Execute rollback commands
- [ ] Verify service health
- [ ] Run smoke tests
- [ ] Monitor performance
- [ ] Restore traffic
- [ ] Validate functionality
- [ ] Update monitoring

### Post-Rollback Checklist
- [ ] Document rollback incident
- [ ] Analyze root cause
- [ ] Update procedures
- [ ] Notify stakeholders
- [ ] Schedule post-mortem
- [ ] Update monitoring alerts
- [ ] Review rollback procedures

## 📚 Communication Templates

### Rollback Notification
```markdown
# Rollback Notification

## Incident Summary
- **Incident ID**: INC-001
- **Time**: [Timestamp]
- **Trigger**: [Rollback trigger]
- **Impact**: [Description of impact]

## Rollback Details
- **From Version**: [Previous version]
- **To Version**: [Target version]
- **Duration**: [Rollback duration]
- **Services Affected**: [List of services]

## Current Status
- **Status**: [Current status]
- **Health Check**: [Health check results]
- **Performance**: [Performance metrics]
- **User Impact**: [User impact assessment]

## Next Steps
- [ ] Root cause analysis
- [ ] Incident report
- [ ] Procedure updates
- [ ] Stakeholder notification

## Contact Information
- **On-call Engineer**: [Name and contact]
- **Team Lead**: [Name and contact]
- **Stakeholders**: [List of stakeholders]
```

### Emergency Notification
```markdown
# EMERGENCY ROLLBACK NOTIFICATION

## Emergency Summary
- **Time**: [Timestamp]
- **Severity**: CRITICAL
- **Action**: Emergency rollback executed
- **Impact**: [Description of impact]

## Rollback Details
- **From Version**: [Previous version]
- **To Version**: [Target version]
- **Duration**: [Rollback duration]

## Current Status
- **Services**: [Service status]
- **Users**: [User impact]
- **Monitoring**: [Monitoring status]

## Immediate Actions
- [ ] Verify service functionality
- [ ] Monitor system performance
- [ ] Check error rates
- [ ] Validate user access

## Follow-up Required
- Root cause analysis
- Incident report
- Procedure review
- Team notification
```

## 🔧 Testing Rollback Procedures

### Rollback Testing
```bash
#!/bin/bash
# scripts/test-rollback.sh

echo "Testing rollback procedures..."

# Test environment setup
./scripts/setup-test-environment.sh

# Test application rollback
echo "Testing application rollback..."
./scripts/app-rollback.sh test-version frontend
./scripts/app-rollback.sh test-version backend

# Test database rollback
echo "Testing database rollback..."
./scripts/database-rollback.sh test-revision

# Test health checks
echo "Testing health checks..."
./scripts/health-check.sh all

# Test emergency rollback
echo "Testing emergency rollback..."
./scripts/emergency-rollback.sh

echo "Rollback testing completed"
```

### Rollback Validation
```bash
#!/bin/bash
# scripts/validate-rollback.sh

echo "Validating rollback procedures..."

# Check rollback scripts exist
REQUIRED_SCRIPTS=(
    "app-rollback.sh"
    "database-rollback.sh"
    "full-rollback.sh"
    "health-check.sh"
    "emergency-rollback.sh"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ ! -f "scripts/$script" ]; then
        echo "ERROR: Required script $script not found"
        exit 1
    fi
done

# Test script permissions
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ ! -x "scripts/$script" ]; then
        echo "ERROR: Script $script is not executable"
        exit 1
    fi
done

# Test backup procedures
echo "Testing backup procedures..."
./scripts/create-backup.sh

# Test monitoring
echo "Testing monitoring..."
./scripts/health-check.sh all

echo "Rollback validation completed successfully"
```

## 📚 Best Practices

### 1. Rollback Planning

1. **Test Regularly**: Test rollback procedures frequently
2. **Document Everything**: Document all rollback procedures
3. **Automate**: Automate rollback where possible
4. **Monitor**: Monitor rollback processes
5. **Communicate**: Clear communication during rollbacks

### 2. Risk Management

1. **Backup Strategy**: Always backup before rollback
2. **Validation**: Validate rollback success
3. **Monitoring**: Monitor during and after rollback
4. **Escalation**: Clear escalation procedures
5. **Documentation**: Document rollback incidents

### 3. Continuous Improvement

1. **Post-Mortems**: Conduct post-mortem analysis
2. **Procedure Updates**: Update procedures based on lessons learned
3. **Training**: Train team on rollback procedures
4. **Automation**: Increase automation over time
5. **Monitoring**: Improve monitoring and alerting

---

*For monitoring information, see [monitoring.md](monitoring.md).*
