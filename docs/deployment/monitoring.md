# Application Monitoring

This document describes monitoring and observability for the React Login Application.

## 🎯 Purpose

Application monitoring provides:
- Real-time performance insights
- Proactive issue detection
- User experience tracking
- System health visibility

## 📊 Monitoring Stack

### 1. Infrastructure Monitoring

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'react-app'
    static_configs:
      - targets: ['backend:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Alert Rules
```yaml
# alert_rules.yml
groups:
  - name: react_app_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database has {{ $value }} active connections"

      - alert: DiskSpaceHigh
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space high"
          description: "Disk usage is {{ $value | humanizePercentage }}"
```

### 2. Application Metrics

#### Backend Metrics (Flask)
```python
# backend/middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Flask, request, Response
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')
LOGIN_ATTEMPTS = Counter('login_attempts_total', 'Total login attempts', ['status'])
USER_REGISTRATIONS = Counter('user_registrations_total', 'Total user registrations')

def setup_metrics(app: Flask):
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            REQUEST_DURATION.observe(duration)
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()
        
        return response
    
    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(), mimetype='text/plain')
```

#### Frontend Metrics (React)
```javascript
// frontend/src/utils/metrics.js
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send metrics to your analytics endpoint
  fetch('/api/metrics', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(metric),
  });
}

// Initialize performance monitoring
getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);

// Custom metrics
class PerformanceMonitor {
  static trackPageLoad(pageName) {
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    this.sendMetric('page_load_time', loadTime, { page: pageName });
  }

  static trackApiCall(endpoint, duration, status) {
    this.sendMetric('api_call_duration', duration, { endpoint, status });
  }

  static trackUserAction(action) {
    this.sendMetric('user_action', 1, { action });
  }

  static sendMetric(name, value, labels = {}) {
    fetch('/api/metrics', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name,
        value,
        labels,
        timestamp: Date.now(),
      }),
    });
  }
}

export default PerformanceMonitor;
```

### 3. Logging Configuration

#### Structured Logging (Python)
```python
# backend/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('/app/logs/app.log')
        ]
    )
    
    # Set JSON formatter for all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(JSONFormatter())
```

#### Frontend Error Logging
```javascript
// frontend/src/utils/errorLogger.js
class ErrorLogger {
  static init() {
    // Global error handler
    window.addEventListener('error', (event) => {
      this.logError({
        type: 'javascript_error',
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack,
      });
    });

    // Unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.logError({
        type: 'unhandled_promise_rejection',
        message: event.reason?.message || event.reason,
        stack: event.reason?.stack,
      });
    });
  }

  static logError(error) {
    const errorData = {
      ...error,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    };

    // Send to backend
    fetch('/api/errors', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorData),
    }).catch(console.error);
  }

  static logUserAction(action, data = {}) {
    const actionData = {
      type: 'user_action',
      action,
      data,
      timestamp: new Date().toISOString(),
      url: window.location.href,
    };

    fetch('/api/user-actions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(actionData),
    }).catch(console.error);
  }
}

export default ErrorLogger;
```

## 📈 Visualization

### 1. Grafana Dashboards

#### Application Dashboard
```json
{
  "dashboard": {
    "title": "React Application Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "singlestat",
        "targets": [
          {
            "expr": "pg_stat_activity_count"
          }
        ]
      }
    ]
  }
}
```

#### System Dashboard
```json
{
  "dashboard": {
    "title": "System Resources Dashboard",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Disk Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_filesystem_free_bytes / node_filesystem_size_bytes)) * 100",
            "legendFormat": "{{instance}} {{mountpoint}}"
          }
        ]
      },
      {
        "title": "Network Traffic",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total[5m])",
            "legendFormat": "RX {{instance}}"
          },
          {
            "expr": "rate(node_network_transmit_bytes_total[5m])",
            "legendFormat": "TX {{instance}}"
          }
        ]
      }
    ]
  }
}
```

### 2. Alerting Setup

#### Alertmanager Configuration
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourdomain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://localhost:5001/webhook'

  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@yourdomain.com'
        subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: 'Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

  - name: 'warning-alerts'
    email_configs:
      - to: 'team@yourdomain.com'
        subject: '[WARNING] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
```

## 🔧 Monitoring Stack Deployment

### Docker Compose Monitoring
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./monitoring/alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    ports:
      - "9187:9187"
    environment:
      - DATA_SOURCE_NAME=postgresql://postgres:password@db:5432/postgres?sslmode=disable
    depends_on:
      - db

  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    ports:
      - "9113:9113"
    command:
      - '-nginx.scrape-uri=http://nginx:8080/stub_status'

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
```

## 📊 Health Checks

### Application Health
```python
# backend/health.py
from flask import Blueprint, jsonify
from database import get_db
import redis
import time

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    checks = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database health check
    try:
        db = next(get_db())
        db.execute('SELECT 1')
        checks['checks']['database'] = 'healthy'
    except Exception as e:
        checks['checks']['database'] = f'unhealthy: {str(e)}'
        checks['status'] = 'unhealthy'
    
    # Redis health check
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        r.ping()
        checks['checks']['redis'] = 'healthy'
    except Exception as e:
        checks['checks']['redis'] = f'unhealthy: {str(e)}'
        checks['status'] = 'unhealthy'
    
    status_code = 200 if checks['status'] == 'healthy' else 503
    return jsonify(checks), status_code

@health_bp.route('/ready')
def readiness_check():
    # Check if application is ready to serve traffic
    return jsonify({'status': 'ready'}), 200

@health_bp.route('/live')
def liveness_check():
    # Check if application is alive
    return jsonify({'status': 'alive'}), 200
```

## 🚨 Incident Response

### 1. Alert Triage

#### Severity Levels
- **Critical**: Service down, data loss, security breach
- **Warning**: Performance degradation, high error rates
- **Info**: Informational, scheduled maintenance

#### Response Procedures
```bash
#!/bin/bash
# scripts/incident-response.sh

ALERT_TYPE=$1
SEVERITY=$2

case $ALERT_TYPE in
  "high_error_rate")
    echo "High error rate detected - Severity: $SEVERITY"
    # Check application logs
    docker-compose logs -f backend | grep ERROR
    # Check system resources
    docker stats
    # Restart services if needed
    docker-compose restart backend
    ;;
  "high_response_time")
    echo "High response time detected - Severity: $SEVERITY"
    # Check database performance
    docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"
    # Check application performance
    curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/health
    ;;
  "database_connections_high")
    echo "High database connections - Severity: $SEVERITY"
    # Check active connections
    docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
    # Kill long-running queries
    docker-compose exec db psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '5 minutes';"
    ;;
esac
```

### 2. Post-Incident Analysis

#### Incident Report Template
```markdown
# Incident Report

## Summary
- **Incident ID**: INC-001
- **Date**: [Date]
- **Duration**: [Start time] - [End time]
- **Impact**: [Description of impact]
- **Severity**: [Critical/Warning/Info]

## Timeline
- [Time]: [Event description]
- [Time]: [Action taken]
- [Time]: [Resolution]

## Root Cause
[Analysis of what caused the incident]

## Resolution
[Steps taken to resolve the incident]

## Prevention
[Measures to prevent recurrence]

## Lessons Learned
[Key takeaways and improvements]
```

## 📚 Best Practices

### 1. Monitoring Strategy

1. **Golden Signals**: Monitor latency, traffic, errors, saturation
2. **SLI/SLO**: Define service level indicators and objectives
3. **Redundancy**: Multiple monitoring systems
4. **Automation**: Automated alerting and response
5. **Documentation**: Comprehensive monitoring documentation

### 2. Alert Management

1. **Meaningful Alerts**: Actionable and relevant alerts
2. **Alert Fatigue**: Avoid unnecessary alerts
3. **Escalation**: Proper escalation procedures
4. **Documentation**: Document alert procedures
5. **Review**: Regular alert review and optimization

### 3. Performance Monitoring

1. **Real User Monitoring**: Track actual user experience
2. **Synthetic Monitoring**: Proactive performance testing
3. **Database Monitoring**: Database performance metrics
4. **Infrastructure Monitoring**: System resource monitoring
5. **Application Monitoring**: Application-specific metrics

---

*For rollback procedures, see [rollback.md](rollback.md).*
