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

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@yourdomain.com'
        subject: '[Alert] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
    
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        title: 'Application Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

# Dashboards

## 1. Dashboard da Aplicação

### Métricas Chave
- Taxa de pedidos
- Taxa de erros
- Percentis de tempo de resposta
- Utilizadores ativos

### Configuração Dashboard Grafana
```json
{
  "dashboard": {
    "title": "React Login Application",
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
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx Errors"
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
          }
        ]
      }
    ]
  }
}
```

## 2. Dashboard de Infraestrutura

### Métricas do Sistema
- Uso de CPU
- Uso de memória
- Uso de disco
- I/O de rede

### Dashboard da Base de Dados
- Performance de queries
- Contagem de conexões
- Tamanho da base de dados
- Eficiência de índices

# Configuração

## 1. Docker Compose Monitorização

### Stack Completa de Monitorização
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=15d'
      - '--web.enable-lifecycle'
    depends_on:
      - alertmanager

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    environment:
      - DATA_SOURCE_NAME=postgresql://user:password@db:5432/appdb
    ports:
      - "9187:9187"
    depends_on:
      - db

  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    ports:
      - "9113:9113"
    depends_on:
      - nginx

volumes:
  prometheus_data:
  alertmanager_data:
  grafana_data:
```

# Métricas de Performance

## 1. Performance da Aplicação

### Indicadores Chave de Performance (KPIs)
| Métrica | Alvo | Medição |
|---------|------|---------|
| Tempo de Resposta (95º percentil) | < 500ms | Duração de pedido HTTP |
| Taxa de Erro | < 1% | Respostas HTTP 5xx |
| Throughput | > 100 req/s | Pedidos por segundo |
| Disponibilidade | > 99.9% | Percentagem de uptime |

### Limiares de Performance
```yaml
# Limiares de performance
performance_thresholds:
  response_time_p95: 500ms
  response_time_p99: 1000ms
  error_rate: 1%
  throughput: 100 req/s
  availability: 99.9%
```

## 2. Métricas de Infraestrutura

### Utilização de Recursos
| Métrica | Aviso | Crítico | Medição |
|---------|--------|----------|---------|
| Uso de CPU | 80% | 95% | Percentagem de CPU do sistema |
| Uso de Memória | 85% | 95% | Percentagem de memória do sistema |
| Uso de Disco | 85% | 95% | Percentagem de espaço em disco |
| I/O de Rede | 80% | 95% | Uso de largura de banda de rede |

# Manutenção

## 1. Manutenção da Monitorização

### Tarefas Regulares
```bash
# Verificar saúde do sistema de monitorização
curl http://localhost:9090/-/healthy

# Backup de dados Prometheus
docker exec prometheus tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz /prometheus

# Limpar métricas antigas
docker exec prometheus promtool tsdb delete --start=$(date -d '30 days ago' --iso-8601) /prometheus
```

# Resposta a Incidentes

## 1. Triagem de Alertas

### Priorização de Alertas
1. **Crítico**: Serviço em baixo, perda de dados, breach de segurança
2. **Alto**: Degradação de performance, interrupção parcial
3. **Médio**: Avisos de recursos, issues não críticos
4. **Baixo**: Alertas informativos, avisos de manutenção

### Procedimentos de Resposta
```bash
# Verificar status do serviço
docker-compose ps

# Verificar logs recentes
docker-compose logs --since=1h backend

# Verificar recursos do sistema
docker stats

# Verificar conectividade de rede
curl -f http://localhost:5000/health
```

# Boas Práticas

## 1. Estratégia de Monitorização

1. **Cobertura Abrangente**: Monitorizar todos os componentes críticos
2. **Métricas Significativas**: Rastrear métricas que importam
3. **Alertas Acionáveis**: Criar alertas que requerem ação
4. **Revisão Regular**: Rever e atualizar monitorização regularmente
5. **Documentação**: Documentar todos os procedimentos de monitorização

## 2. Gestão de Alertas

1. **Ajuste de Limiares**: Definir limiares de alerta adequados
2. **Fadiga de Alertas**: Evitar muitos falsos positivos
3. **Caminhos de Escalação**: Definir procedimentos claros de escalação
4. **Testes**: Testar sistemas de alerta regularmente
5. **Documentação**: Documentar procedimentos de alerta

---
