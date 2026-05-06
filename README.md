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

# Backend
1. Navegar para o diretorio backend:
   ```bash
   cd backend
   ```

2. Instalar dependencias Python:
   ```bash
   pip install -r requirements.txt
   ```

3. Iniciar o servidor Flask:
   ```bash
   python app.py
   ```
   O backend ira correr em http://localhost:5000

# Frontend
1. Navegar para o diretorio frontend:
   ```bash
   cd frontend
   ```

2. Instalar dependencias Node.js:
   ```bash
   npm install
   ```

3. Iniciar o servidor de desenvolvimento React:
   ```bash
   npm start
   ```
   O frontend ira correr em http://localhost:3000

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