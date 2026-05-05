# Desenvolvimento Local com Docker

Este documento descreve como configurar e executar a aplicação React Login localmente usando Docker.

## Propósito

O desenvolvimento local com Docker proporciona:
- Ambiente de desenvolvimento consistente
- Dependências isoladas
- Configuração e desmontagem fáceis
- Ambiente semelhante ao de produção

## Pré-requisitos

### Software Necessário

- **Docker**: Versão 20.10 ou posterior
- **Docker Compose**: Versão 2.0 ou posterior
- **Git**: Para clonar o repositório

### Requisitos do Sistema

- **RAM**: Mínimo 4GB, recomendado 8GB
- **Armazenamento**: Mínimo 10GB de espaço livre
- **Sistema Operacional**: Windows 10/11, macOS 10.15+, ou Linux

## Início Rápido

### 1. Clonar Repositório

```bash
git clone https://github.com/your-username/react-login-app.git
cd react-login-app
```

### 2. Configuração do Ambiente

Crie um ficheiro `.env` no diretório raiz:

```bash
# Configuração da Base de Dados
DATABASE_URL=sqlite:///./app.db

# Configuração da Aplicação
FLASK_ENV=development
FLASK_DEBUG=True

# Configuração do Frontend
REACT_APP_API_URL=http://localhost:5000
```

### 3. Iniciar Ambiente de Desenvolvimento

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### 4. Acessar Aplicações

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Verificação de Saúde**: http://localhost:5000/health

## Configuração Docker Compose

### Serviços

#### Serviço Frontend
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  volumes:
    - ./frontend:/app
    - /app/node_modules
  environment:
    - REACT_APP_API_URL=http://localhost:5000
  depends_on:
    - backend
```

**Propósito**: Servidor de desenvolvimento React
**Volumes**: Montagem de código ao vivo para desenvolvimento
**Ambiente**: Configuração do endpoint API

#### Serviço Backend
```yaml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
  ports:
    - "5000:5000"
  volumes:
    - ./backend:/app
  environment:
    - FLASK_ENV=development
    - FLASK_DEBUG=True
    - DATABASE_URL=sqlite:///./app.db
  depends_on:
    - db
```

**Propósito**: Servidor de desenvolvimento Flask
**Volumes**: Montagem de código ao vivo para desenvolvimento
**Ambiente**: Configuração de desenvolvimento

#### Serviço Base de Dados
```yaml
db:
  image: sqlite:latest
  volumes:
    - ./data:/data
  environment:
    - SQLITE_DATABASE=app.db
```

**Propósito**: Base de dados SQLite
**Volumes**: Armazenamento de dados persistente
**Ambiente**: Configuração da base de dados

## Workflow de Desenvolvimento

### 1. Fazer Alterações

#### Alterações no Frontend
```bash
# Frontend recarrega automaticamente
# Alterações em ./frontend são refletidas imediatamente
```

#### Alterações no Backend
```bash
# Backend recarrega automaticamente em desenvolvimento
# Alterações em ./backend são refletidas imediatamente
```

#### Alterações na Base de Dados
```bash
# Acessar contentor da base de dados
docker-compose exec backend python
from database import engine, Base
Base.metadata.create_all(bind=engine)
```

### 2. Testes

#### Executar Testes
```bash
# Testes frontend
docker-compose exec frontend npm test

# Testes backend
docker-compose exec backend python -m pytest testes/

# Testes de integração
docker-compose exec frontend npm test -- --testPathPattern=integration
```

#### Cobertura de Testes
```bash
# Cobertura frontend
docker-compose exec frontend npm test -- --coverage

# Cobertura backend
docker-compose exec backend python -m pytest --cov=app testes/
```

### 3. Depuração

#### Ver Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db
```

#### Acessar Contentores
```bash
# Contentor frontend
docker-compose exec frontend sh

# Contentor backend
docker-compose exec backend sh

# Contentor base de dados
docker-compose exec db sh
```

## Configuração

### Variáveis de Ambiente

#### Frontend (.env)
```bash
# Configuração da API
REACT_APP_API_URL=http://localhost:5000

# Configurações de Desenvolvimento
REACT_APP_ENV=development
GENERATE_SOURCEMAP=true
```

#### Backend (.env)
```bash
# Configuração Flask
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=app.py

# Configuração da Base de Dados
DATABASE_URL=sqlite:///./app.db

# Configuração de Segurança
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

## Troubleshooting

### Issues Comuns

#### 1. Conflitos de Porta
```bash
# Verificar uso de portas
netstat -tulpn | grep :3000
netstat -tulpn | grep :5000

# Matar processos
sudo kill -9 <PID>
```

#### 2. Issues de Montagem de Volume
```bash
# Verificar montagens de volume
docker-compose config

# Reconstruir contentores
docker-compose down
docker-compose up --build
```

#### 3. Issues de Permissão
```bash
# Corrigir permissões de ficheiros
sudo chown -R $USER:$USER .

# Reiniciar permissões Docker
sudo usermod -aG docker $USER
newgrp docker
```

---

*Para deploy de produção, ver [production-deployment.md](production-deployment.md).*
