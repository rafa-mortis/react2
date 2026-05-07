# Funcionalidades

# Backend
- Sistema de autenticacao com base de dados SQLite
- Tres tipos de utilizadores: normal, admin, guest
- Passwords encriptadas com SHA256
- Protecao completa contra SQL Injection
- Validacao e sanitizacao de inputs
- Rate limiting por IP
- CORS seguro e restrito
- Testes unitarios e de seguranca

# Frontend
- Interface de login responsiva
- Validacao de email no frontend
- Gestao de estado com React hooks
- Suporte para diferentes tipos de utilizador
- Testes unitarios, de integracao e end-to-end
- Mensagens de erro em portugues

# Instalacao e Configuracao

## Pré-requisitos do Sistema
Antes de iniciar, certifique-se de que tem as seguintes ferramentas instaladas:

```bash
# Verificar versoes minimas requeridas
python --version  # Python 3.13+
node --version    # Node.js 18+
npm --version     # npm 8+
docker --version  # Docker 20+
git --version     # Git 2.30+
```

## Configuracao Completa do Ambiente

### Passo 1: Clonar o Repositorio
```bash
git clone https://github.com/rafa-mortis/react2.git
cd react2
```

### Passo 2: Configuracao do Backend
1. Navegar para o diretorio backend:
   ```bash
   cd backend
   ```

2. Criar ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. Instalar dependencias Python:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Verificar instalacao:
   ```bash
   python app.py &
   curl http://localhost:5000/health
   # Deve retornar status 200
   ```

### Passo 3: Configuracao do Frontend
1. Navegar para o diretorio frontend:
   ```bash
   cd ../frontend
   ```

2. Instalar dependencias Node.js:
   ```bash
   npm install
   ```

3. Verificar instalacao:
   ```bash
   npm run build
   npm start &
   # O frontend ira correr em http://localhost:3000
   ```

### Passo 4: Validacao do Sistema Completo
1. Iniciar ambos os servidores:
   ```bash
   # Terminal 1 (Backend)
   cd backend && python app.py

   # Terminal 2 (Frontend)  
   cd frontend && npm start
   ```

2. Testar integracao:
   - Aceder a http://localhost:3000
   - Tentar login com: user@gmail.com / 123456
   - Verificar comunicacao com backend nos logs

## Configuracao com Docker (Alternativa)
Para uma configuracao mais rapida usando Docker:

```bash
# Build e iniciar todos os servicos
docker-compose up --build

# Verificar estado dos servicos
docker-compose ps

# Parar servicos
docker-compose down
```

## GitHub Actions - Setup Automatizado

### Configuracao Inicial
O projeto ja vem com pipelines de CI/CD configurados. Para ativar:

1. **No repositorio GitHub:**
   - Va para Settings > Actions > General
   - Ative "Allow all actions" e "Allow fork pull requests"
   - Configure permissions para "Read and write permissions"

2. **Workflows Disponiveis:**
   - `frontend.yml` - Pipeline do frontend React
   - `backend.yml` - Pipeline do backend Python/Flask  
   - `deploy.yml` - Simulacao de deployment

### Execucao dos Workflows
Os pipelines sao executados automaticamente:

```bash
# Development (branch github-actions)
git push origin github-actions
# → Executa: frontend-ci, backend-ci, security-scan, code-quality

# Production (branch main)
git push origin main
# → Executa: todos os pipelines + deploy-simulation
```

### Testes Locais com GitHub Actions
Para testar workflows localmente antes do push:

```bash
# Instalar act (GitHub Actions runner)
# Windows:
choco install act
# Mac:
brew install act
# Linux:
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Testar workflow especifico
act -j frontend-ci      # Testa pipeline do frontend
act -j backend-ci       # Testa pipeline do backend
act -j security-scan    # Testa scan de seguranca
act -j deploy-simulation # Testa deployment

# Testar todos os workflows
act -W .github/workflows/frontend.yml
act -W .github/workflows/backend.yml
```

### Monitoramento dos Pipelines
Acompanhe a execucao dos workflows em:
1. GitHub > Actions > selecionar workflow
2. Verificar logs detalhados de cada step
3. Download dos artefatos gerados

## Resumo do Fluxo de Instalacao

### Metodo 1: Desenvolvimento Local
```bash
git clone https://github.com/rafa-mortis/react2.git
cd react2

# Backend
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python app.py

# Frontend (novo terminal)
cd frontend
npm install
npm start
```

### Metodo 2: Docker (Recomendado)
```bash
git clone https://github.com/rafa-mortis/react2.git
cd react2
docker-compose up --build
```

### Metodo 3: CI/CD Automatizado
```bash
git clone https://github.com/rafa-mortis/react2.git
cd react2
git checkout github-actions
# Fazer alteracoes e push para testar pipelines automaticos
git push origin github-actions
```

**Importante:** Todos os metodos de instalacao foram testados e garantem o funcionamento correto da aplicacao. Escolha o metodo que melhor se adapta ao seu ambiente de desenvolvimento.

# Utilizacao

# Criar Utilizadores de Teste
A base de dados ja vem com utilizadores de teste pre-criados:
- Normal User: user@gmail.com / 123456
- Admin User: admin@gmail.com / admin123
- Guest User: guest@gmail.com / guest123

# Endpoints da API
- POST /login - Autenticacao de utilizadores
- POST /register - Registo de novos utilizadores
- POST /admin/create - Criar utilizadores admin
- GET /guest - Acesso de visitante sem autenticacao
- GET /health - Verificacao de saude do servidor

# Testes
- Testes unitarios: npm test src/unit.test.js
- Testes de integracao: npm test src/integration.test.js
- Testes end-to-end: npx playwright test e2e.test.js
- Testes de seguranca: python test_security.py
- Testes da base de dados: python test_database.py

# Seguranca

# Protecoes Implementadas
- SQL Injection: Queries parametrizadas e deteccao de padroes
- Validacao de Inputs: Email, password e role validados
- Sanitizacao: Remocao de caracteres perigosos
- Rate Limiting: Limites de requisicoes por IP
- CORS: Apenas origens e metodos permitidos
- Password Hashing: SHA256 para armazenamento seguro

# Testes de Seguranca
O sistema inclui testes comprehensive para:
- Validacao de formatos de email
- Validacao de requisitos de password
- Deteccao de tentativas de SQL Injection
- Eficacia da sanitizacao de inputs
- Protecoes contra ataques comuns

# Base de Dados

### Schema
Tabela users com as seguintes colunas:
- id: Chave primaria auto-incremento
- email: Email unico do utilizador (max 120 caracteres)
- password: Password encriptada SHA256 (max 255 caracteres)
- role: Tipo de utilizador (normal, admin, guest)

# Operacoes SQL
- Login: SELECT com parametros seguros
- Registo: INSERT com validacao de duplicados
- Consultas: Uso exclusivo de queries parametrizadas

# Desenvolvimento

# Tecnologias Utilizadas
- Backend: Python 3.13, Flask 2.3.3, SQLAlchemy 2.0.35
- Frontend: React, JavaScript ES6+, HTML5, CSS3
- Base de Dados: SQLite
- Testes: Jest, Playwright, pytest
- Seguranca: Flask-CORS, hashlib, re (regex)

# Padroes e Boas Praticas
- Separacao clara entre frontend e backend
- Validacao de dados em ambos os lados
- Tratamento de erros adequado
- Logging detalhado para debugging
- Testes comprehensive em todos os niveis
- Comentarios em portugues de Portugal

# GitHub Actions CI/CD

## Visao Geral
O projeto utiliza pipelines automatizados de CI/CD com GitHub Actions para garantir qualidade e seguranca no desenvolvimento e deployment.

## Workflows Configurados

### Frontend Pipeline (.github/workflows/frontend.yml)
**Triggers:**
- Push para branches main ou github-actions com mudanças em frontend/
- Pull requests para main com mudanças em frontend/

**Etapas:**
1. **Setup Node.js 18** - Configuracao do ambiente Node.js
2. **Install Dependencies** - Instalacao com npm ci para cache otimizado
3. **Security Audit** - Verificacao de vulnerabilidades com npm audit
4. **Unit Tests** - Testes unitarios com coverage
5. **Integration Tests** - Testes de integracao
6. **Build Application** - Build de producao do React
7. **Docker Validation** - Build e teste da imagem Docker
8. **Playwright Tests** - Testes end-to-end

### Backend Pipeline (.github/workflows/backend.yml)
**Triggers:**
- Push para branches main ou github-actions com mudanças em backend/
- Pull requests para main com mudanças em backend/

**Etapas:**
1. **Setup Python 3.13** - Configuracao do ambiente Python
2. **Install Dependencies** - Instalacao via requirements.txt
3. **Security Audit** - Scan com safety
4. **Database Tests** - Testes do banco de dados
5. **Security Tests** - Testes de seguranca
6. **Application Tests** - Testes gerais da aplicacao
7. **Docker Validation** - Build e teste da imagem Docker
8. **Security Scan** - Scan de vulnerabilidades com Trivy
9. **Code Quality** - Linting e formatacao com flake8/black/isort

### Deploy Simulation (.github/workflows/deploy.yml)
**Triggers:**
- Push para branch main
- Pull requests merged para main

**Etapas:**
1. **Docker Compose Build** - Build de todos os servicos
2. **Deployment Startup** - Inicializacao dos servicos
3. **Health Checks** - Verificacao de saude dos servicos
4. **Integration Tests** - Testes de integracao da aplicacao
5. **Deployment Report** - Geracao de relatorio detalhado
6. **Production Simulation** - Simulacao de deployment prod

## Configuracao Local

### Pré-requisitos
```bash
# Git
git --version

# Docker
docker --version
docker-compose --version

# Node.js (para frontend)
node --version
npm --version

# Python (para backend)
python --version
pip --version
```

### Testar Workflows Localmente
```bash
# Instalar act (GitHub Actions runner)
# Windows: choco install act
# Mac: brew install act
# Linux: https://github.com/nektos/act

# Testar workflow especifico
act -j frontend-ci
act -j backend-ci
act -j deploy-simulation

# Testar todos os workflows
act
```

## Artefatos e Relatorios

### Artefatos Gerados
**Frontend:**
- frontend-build - Build da aplicacao React
- playwright-report - Relatorios dos testes E2E

**Backend:**
- backend-test-results - Resultados dos testes e security scan
- security-scan-results - Relatorios do Trivy

**Deployment:**
- deployment-report-{run_number} - Relatorio completo do deployment
- production-config-{run_number} - Configuracao de producao

### Visualizacao dos Artefatos
1. Acesse o repositorio no GitHub
2. Va para "Actions"
3. Selecione o workflow execution
4. Clique em "Artifacts" para baixar os relatorios

## Seguranca Implementada

### Scans Automaticos
1. **Frontend:**
   - npm audit - Vulnerabilidades de pacotes npm
   - Playwright security tests

2. **Backend:**
   - safety - Vulnerabilidades de pacotes Python
   - Trivy - Scan de vulnerabilidades de container
   - Testes de seguranca customizados

3. **Infrastructure:**
   - Docker security scanning
   - Code quality checks

## Fluxo de Deployment

### Development Workflow
1. Developer Push → Feature Branch
2. CI Pipeline → Tests Pass
3. Pull Request → Code Review
4. Merge to main → Deploy Simulation

### Pipeline Triggers
1. **Development:**
   - Push para github-actions → CI pipelines
   - Pull requests → CI + validation

2. **Production:**
   - Push para main → Deploy simulation
   - Merge PR → Production simulation

## Troubleshooting

### Problemas Comuns
**Falha no Cache do npm**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Falha no Docker Build**
```bash
docker system prune -a
docker-compose build --no-cache
```

**Falha nos Testes**
- Verificar logs completos no workflow execution
- Baixar artefatos para analise detalhada
- Rodar testes localmente com act

## Manutencao

# Atualizacao de Dependencias
- Backend: pip install --upgrade -r requirements.txt
- Frontend: npm update

# Monitorizacao
- Logs do servidor Flask mostram operacoes da base de dados
- Testes de seguranca podem ser executados regularmente
- Rate limiting ajuda a prevenir abusos
- GitHub Actions fornecem monitoramento automatizado dos pipelines
- Artefatos de deployment permitem analise post-mortem

# Atualizacao de Workflows
- Revisar versoes das Actions regularmente
- Atualizar versoes de Node.js/Python quando necessario
- Manter documentacao em dia