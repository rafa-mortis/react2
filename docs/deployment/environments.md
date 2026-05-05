# Configurações de Ambiente

## Propósito

Configurações de ambiente proporcionam:
- Ambientes de deploy isolados
- Gestão de configuração consistente
- Configurações específicas de ambiente
- Separação adequada de responsabilidades

## Tipos de Ambiente

# Desenvolvimento

## Propósito
- Desenvolvimento e teste local
- Desenvolvimento de funcionalidades e debugging
- Testes unitários e de integração

## Configuração
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

## Variáveis de Ambiente
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

# Staging

## Propósito
- Teste pré-produção
- Teste de aceitação de utilizador
- Teste de performance
- Teste de integração

## Configuração
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

## Variáveis de Ambiente
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

# Produção

## Propósito
- Deploy de produção em tempo real
- Acesso de utilizador final
- Alta disponibilidade e performance
- Segurança e conformidade

## Configuração
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

## Variáveis de Ambiente
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

# Gestão de Configuração

## Estrutura de Ficheiros
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

## Seleção de Ambiente
```bash
# Desenvolvimento
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.development up -d

# Staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging up -d

# Produção
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.production up -d
```

# Comparação de Ambientes

## Diferenças de Configuração

| Aspecto | Desenvolvimento | Staging | Produção |
|----------|-----------------|----------|-----------|
| **Base de Dados** | SQLite | PostgreSQL | PostgreSQL |
| **Réplicas** | 1 | 1 | Múltiplas |
| **SSL** | HTTP | HTTPS | HTTPS |
| **Logging** | DEBUG | INFO | WARNING |
| **Monitorização** | Básico | Completo | Completo |
| **Backups** | Nenhum | Diário | Tempo real |
| **Segurança** | Mínimo | Padrão | Alta |

## Alocação de Recursos

| Ambiente | CPU | Memória | Armazenamento |
|----------|------|----------|---------------|
| Desenvolvimento | Partilhado | Partilhado | Local |
| Staging | 2 cores | 4GB | 20GB |
| Produção | 8+ cores | 16GB+ | 100GB+ |

# Processo de Deploy

## Promoção de Ambiente

### Desenvolvimento → Staging
```bash
# Build versão desenvolvimento
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# Tag para staging
docker tag react-login-frontend:latest ${DOCKER_USERNAME}/react-login-frontend:staging-${BUILD_NUMBER}
docker tag react-login-backend:latest ${DOCKER_USERNAME}/react-login-backend:staging-${BUILD_NUMBER}

# Deploy para staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging up -d
```

### Staging → Produção
```bash
# Executar testes staging
./scripts/run-staging-tests.sh

# Tag para produção
docker tag ${DOCKER_USERNAME}/react-login-frontend:staging-${BUILD_NUMBER} ${DOCKER_USERNAME}/react-login-frontend:latest
docker tag ${DOCKER_USERNAME}/react-login-backend:staging-${BUILD_NUMBER} ${DOCKER_USERNAME}/react-login-backend:latest

# Deploy para produção
./scripts/deploy-production.sh
```

# Segurança

## Gestão de Secrets

### Desenvolvimento
```bash
# Usar secrets de desenvolvimento
SECRET_KEY=dev-secret-key
DB_PASSWORD=dev-password
```

### Staging
```bash
# Usar secrets de staging
SECRET_KEY=${STAGING_SECRET_KEY}
DB_PASSWORD=${STAGING_DB_PASSWORD}
```

### Produção
```bash
# Usar secrets de produção
SECRET_KEY=${SECRET_KEY}
DB_PASSWORD=${DB_PASSWORD}
```

# Boas Práticas

## Gestão de Ambiente

1. **Consistência**: Manter ambientes o mais semelhantes possível
2. **Isolamento**: Garantir ambientes devidamente isolados
3. **Documentação**: Documentar todas as diferenças de ambiente
4. **Controlo de Versões**: Rastrear configurações de ambiente
5. **Automação**: Automatizar setup e gestão de ambiente

## Segurança

1. **Privilégio Mínimo**: Usar permissões mínimas necessárias
2. **Gestão de Secrets**: Práticas adequadas de gestão de secrets
3. **Isolamento de Rede**: Segmentação de rede adequada
4. **Atualizações Regulares**: Manter dependências atualizadas
5. **Scanning de Segurança**: Avaliações de segurança regulares

---

*Para procedimentos de deploy, ver [monitoring.md](monitoring.md).*
