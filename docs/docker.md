# Docker

## Visão Geral
Implementação de Docker containerização para a aplicação React login.

## Estrutura
- **backend/Dockerfile**: Container Python 3.13 com Flask
- **frontend/Dockerfile**: Container Node.js 18 com React
- **docker-compose.yml**: Orquestração dos serviços

## Comandos
```bash
# Construir e iniciar serviços
docker compose up --build

# Parar serviços
docker compose down

# Verificar status
docker compose ps
```

## Configuração
- **Backend**: Porta 5000, binding 0.0.0.0
- **Frontend**: Porta 3000, proxy para backend
- **Rede**: app-network para comunicação entre containers

## Acesso
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- Health Check: http://localhost:5000/health

## Soluções Aplicadas
- Simplificação do Dockerfile frontend (remoção de user management)
- Correção de binding do backend para 0.0.0.0
- Configuração de proxy do frontend para container hostname
