# Procedimentos de Rollback

## Propósito

Os procedimentos de rollback garantem:
- Continuidade do serviço durante falhas
- Preservação da integridade dos dados
- Downtime mínimo durante rollbacks
- Recuperação rápida de issues de deploy

# Estratégias de Rollback

## 1. Blue-Green Rollback

### Visão Geral da Estratégia
O deploy Blue-Green mantém dois ambientes de produção idênticos:
- **Blue**: Versão de produção atual
- **Green**: Nova versão sendo deployada

### Processo de Rollback
```bash
# Mudar tráfego de volta para ambiente blue
./scripts/switch-traffic.sh blue

# Verificar se ambiente blue está saudável
./scripts/health-check.sh blue

# Reduzir escala do ambiente green
docker-compose -f docker-compose.green.yml down

# Limpar recursos green
docker-compose -f docker-compose.green.yml down -v
```

### Script de Mudança de Tráfego
```bash
#!/bin/bash
# scripts/switch-traffic.sh

ENVIRONMENT=${1:-blue}

if [ "$ENVIRONMENT" != "blue" ] && [ "$ENVIRONMENT" != "green" ]; then
    echo "Usage: $0 [blue|green]"
    exit 1
fi

echo "A mudar tráfego para ambiente $ENVIRONMENT..."

# Atualizar configuração do load balancer
if [ "$ENVIRONMENT" = "blue" ]; then
    # Apontar para ambiente blue
    sed -i 's/server green:/server blue:/' /etc/nginx/nginx.conf
else
    # Apontar para ambiente green
    sed -i 's/server blue:/server green:/' /etc/nginx/nginx.conf
fi

# Recarregar nginx
nginx -s reload

echo "Tráfego mudado para ambiente $ENVIRONMENT"
```

## 2. Rollback da Base de Dados

### Visão Geral da Estratégia
Os procedimentos de rollback da base de dados lidam com:
- Mudanças de schema
- Issues de migração de dados
- Corrupção de dados
- Degradação de performance

### Backup e Restauração da Base de Dados
```bash
# Criar backup da base de dados antes do rollback
docker-compose exec db pg_dump -U appuser appdb > rollback_backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar de backup anterior
docker-compose exec -T db psql -U appuser appdb < previous_backup.sql

# Verificar integridade dos dados
docker-compose exec backend python -c "
from database import engine
result = engine.execute('SELECT COUNT(*) FROM users').scalar()
print(f'Contagem de utilizadores: {result}')
"
```

### Rollback de Migração
```bash
# Rollback de migrações da base de dados
docker-compose exec backend flask db downgrade

# Rollback para versão específica
docker-compose exec backend flask db downgrade -r <revision_id>

# Verificar histórico de migrações
docker-compose exec backend flask db history
```

## 3. Rollback da Aplicação

### Visão Geral da Estratégia
O rollback da aplicação lida com:
- Issues de deploy de código
- Problemas de configuração
- Conflitos de dependências
- Erros de runtime

### Rollback de Imagem Docker
```bash
# Listar tags de imagem disponíveis
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}"

# Marcar versão anterior como latest
docker tag ${DOCKER_USERNAME}/react-login-backend:previous ${DOCKER_USERNAME}/react-login-backend:latest
docker tag ${DOCKER_USERNAME}/react-login-frontend:previous ${DOCKER_USERNAME}/react-login-frontend:latest

# Redeploy com versão anterior
docker-compose down
docker-compose up -d

# Verificar deploy
./scripts/health-check.sh
```

### Rollback de Configuração
```bash
# Restaurar configuração anterior
cp .env.production.backup .env.production

# Restaurar configuração docker-compose
cp docker-compose.prod.yml.backup docker-compose.prod.yml

# Redeploy com configuração restaurada
docker-compose down
docker-compose up -d

# Verificar configuração
docker-compose config
```

# Rollback de Emergência

## 1. Resposta Imediata

### Script de Rollback de Emergência
```bash
#!/bin/bash
# scripts/emergency-rollback.sh

echo "A iniciar rollback de emergência..."

# Parar deploy atual
docker-compose down

# Mudar para configuração de emergência
cp emergency/docker-compose.emergency.yml docker-compose.yml
cp emergency/.env.emergency .env

# Iniciar ambiente de emergência
docker-compose up -d

# Esperar pelos serviços iniciarem
sleep 30

# Verificação de saúde
if ./scripts/health-check.sh; then
    echo "Rollback de emergência bem sucedido"
else
    echo "Rollback de emergência falhou - intervenção manual necessária"
    exit 1
fi
```

### Procedimentos Manuais de Emergência
```bash
# 1. Parar todos os serviços
docker-compose down

# 2. Pull da última imagem boa conhecida
docker pull ${DOCKER_USERNAME}/react-login-backend:stable
docker pull ${DOCKER_USERNAME}/react-login-frontend:stable

# 3. Atualizar docker-compose.yml para usar imagens estáveis
sed -i 's/:latest/:stable/g' docker-compose.yml

# 4. Iniciar serviços
docker-compose up -d

# 5. Verificar saúde
curl -f http://localhost:5000/health
```

## 2. Recuperação de Dados

### Recuperação da Base de Dados
```bash
# Identificar último backup bom
LATEST_BACKUP=$(ls -t backups/database/ | head -1)

# Restaurar base de dados
docker-compose exec -T db psql -U appuser appdb < backups/database/$LATEST_BACKUP

# Verificar integridade dos dados
docker-compose exec backend python scripts/verify_data.py
```

### Recuperação de Estado da Aplicação
```bash
# Restaurar configuração da aplicação
cp backups/config/docker-compose.prod.yml docker-compose.prod.yml
cp backups/config/.env.production .env.production

# Restaurar certificados SSL
cp -r backups/ssl/* /etc/nginx/ssl/

# Reiniciar serviços
docker-compose down
docker-compose up -d
```

# Monitorização de Rollback

## 1. Verificações de Saúde

### Saúde da Aplicação
```bash
#!/bin/bash
# scripts/health-check.sh

ENVIRONMENT=${1:-production}

echo "A verificar saúde do ambiente $ENVIRONMENT..."

# Verificar frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend está saudável"
else
    echo "❌ Frontend está insaludável"
    exit 1
fi

# Verificar backend
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend está saudável"
else
    echo "❌ Backend está insaludável"
    exit 1
fi

# Verificar base de dados
if docker-compose exec db pg_isready -U appuser -d appdb > /dev/null 2>&1; then
    echo "✅ Base de dados está saudável"
else
    echo "❌ Base de dados está insaludável"
    exit 1
fi

echo "Todos os serviços estão saudáveis"
```

### Saúde da Base de Dados
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
