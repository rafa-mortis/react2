# Deploy

## Visão Geral
Processo de deploy automatizado para produção da aplicação React login.

## Ambiente Docker
- **Containers**: Frontend (React) + Backend (Flask)
- **Orquestração**: Docker Compose
- **Images**: Docker Hub registry

## Deploy Local
```bash
# Iniciar ambiente local
docker compose up --build

# Verificar status
docker compose ps

# Acessar aplicação
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

## Deploy Produção
- **Images**: Push para Docker Hub via GitHub Actions
- **Infrastructure**: Docker containers em cloud
- **Monitoring**: Health checks automatizados

## GitHub Actions Deploy
- Trigger automático em push para main
- Build e push de images
- Deploy para staging/produção
- Notificações de status

## Configuração Produção
- Environment variables configuradas
- Health checks ativos
- Logs centralizados
- Backup automático

## Monitoramento
- Health checks: /health endpoint
- Logs: Docker logs + application logs
- Metrics: CPU, memory, network
- Alerts: Notificações automáticas

## Rollback
- Versionamento de Docker images
- Rollback automático em falhas
- Backup de configurações
- Recovery plan documentado

## Melhores Práticas
- Zero-downtime deployment
- Blue-green deployment
- Canary releases
- Automated testing antes do deploy
