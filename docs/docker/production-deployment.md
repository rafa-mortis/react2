# Deploy Docker de Produção

## Propósito

Deploy de produção proporciona:
- Deploy escalável e fiável
- Alta disponibilidade e tolerância a falhas
- Otimização de segurança e performance
- Capacidades de monitorização e logging

## Pré-requisitos

# Requisitos de Infraestrutura

- **Docker Engine**: Versão 20.10 ou posterior
- **Docker Compose**: Versão 2.0 ou posterior
- **Load Balancer**: Nginx, HAProxy, ou cloud load balancer
- **Certificado SSL**: Para terminação HTTPS
- **Monitorização**: Prometheus, Grafana, ou cloud monitoring

# Requisitos de Sistema

- **CPU**: Mínimo 4 cores, recomendado 8 cores
- **RAM**: Mínimo 8GB, recomendado 16GB
- **Armazenamento**: Mínimo 50GB SSD, recomendado 100GB
- **Rede**: Ligação 1Gbps, redundante se possível

# Arquitetura de Deploy

## Arquitetura de Produção

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

## Docker Compose Produção

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

# Configuração

## Variáveis de Ambiente

### Ambiente de Produção (.env.production)
```bash
# Configuração da Aplicação
VERSION=latest
NODE_ENV=production
FLASK_ENV=production

# Configuração da Base de Dados
DATABASE_URL=postgresql://appuser:password@db:5432/appdb
DB_PASSWORD=your-secure-db-password

# Configuração de Segurança
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Configuração SSL
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem

# Configuração de Monitorização
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO
```

# Configuração Nginx

## nginx/nginx.conf
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

        # Login endpoint com rate limiting mais restrito
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

# Processo de Deploy

## Preparação

### Atualizar Imagens Docker
```bash
# Pull imagens mais recentes
docker-compose -f docker-compose.prod.yml pull

# Ou build versão específica
docker-compose -f docker-compose.prod.yml build
```

### Migração da Base de Dados
```bash
# Executar migrações da base de dados
docker-compose -f docker-compose.prod.yml run --rm backend flask db upgrade

# Criar dados iniciais se necessário
docker-compose -f docker-compose.prod.yml run --rm backend python scripts/init_data.py
```

## Deploy

### Deploy da Aplicação
```bash
# Deploy para produção
docker-compose -f docker-compose.prod.yml up -d

# Verificar status dos serviços
docker-compose -f docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Verificações de Saúde
```bash
# Verificar saúde da aplicação
curl https://yourdomain.com/api/health

# Verificar conectividade da base de dados
docker-compose -f docker-compose.prod.yml exec backend python -c "from database import engine; print(engine.execute('SELECT 1').scalar())"
```

## Pós-Deploy

### Verificação
```bash
# Testar funcionalidade de login
curl -X POST https://yourdomain.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}'

# Verificar certificado SSL
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### Configuração de Monitorização
```bash
# Configurar monitorização
docker-compose -f docker-compose.monitoring.yml up -d

# Verificar métricas
curl http://localhost:9090/metrics
```

# Monitorização e Logging

## Monitorização da Aplicação

### Verificações de Saúde
```bash
# Saúde da aplicação
curl https://yourdomain.com/api/health

# Saúde da base de dados
docker-compose exec db pg_isready -U appuser -d appdb

# Saúde do Redis
docker-compose exec redis redis-cli ping
```

### Coleção de Métricas
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

## Logging

### Logs da Aplicação
```bash
# Ver logs da aplicação
docker-compose logs -f backend
docker-compose logs -f frontend

# Ver logs nginx
docker-compose logs -f nginx

# Ver logs da base de dados
docker-compose logs -f db
```

# Segurança

## Segurança de Contentores

### Scanning de Segurança
```bash
# Scannear imagens para vulnerabilidades
docker scan ${DOCKER_USERNAME}/react-login-frontend:${VERSION}
docker scan ${DOCKER_USERNAME}/react-login-backend:${VERSION}
```

## Segurança de Rede

### Configuração de Firewall
```bash
# Permitir apenas portas necessárias
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Configuração SSL
```bash
# Gerar certificado SSL
certbot --nginx -d yourdomain.com

# Renovação automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

# Troubleshooting

## Issues Comuns

### 1. Issues de Inicialização de Contentores
```bash
# Ver logs dos contentores
docker-compose logs backend

# Ver status dos contentores
docker-compose ps

# Reiniciar serviços
docker-compose restart backend
```

### 2. Issues de Conexão da Base de Dados
```bash
# Verificar conectividade da base de dados
docker-compose exec db pg_isready -U appuser -d appdb

# Ver logs da base de dados
docker-compose logs db

# Reiniciar conexão da base de dados
docker-compose restart db
```

### 3. Issues de Certificado SSL
```bash
# Verificar certificado SSL
openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout

# Verificar expiração do certificado
openssl x509 -in /etc/nginx/ssl/cert.pem -noout -dates

# Renovar certificado
certbot renew
```

# Boas Práticas

## Práticas de Deploy

1. **Blue-Green Deployment**: Deploys sem downtime
2. **Estratégia de Rollback**: Ter sempre procedimentos de rollback
3. **Verificações de Saúde**: Monitorização de saúde abrangente
4. **Limites de Recursos**: Definir limites de recursos adequados
5. **Estratégia de Backup**: Backups regulares e testes

## Práticas de Segurança

1. **Privilégio Mínimo**: Permissões e acesso mínimos
2. **Gestão de Secrets**: Usar ferramentas de gestão de secrets
3. **Isolamento de Rede**: Segmentação de rede adequada
4. **Atualizações Regulares**: Manter dependências atualizadas
5. **Scanning de Segurança**: Scans de vulnerabilidade regulares

---