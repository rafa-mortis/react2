# Conteúdo da Wiki GitHub para Projeto React Login

## Página Inicial

# Aplicação React Login

Uma aplicação web segura com autenticação de utilizador, controlo de acesso baseado em roles e funcionalidades de segurança abrangentes.

## Início Rápido

### Pré-requisitos
- Node.js 18+
- Python 3.13
- Docker Desktop

### Desenvolvimento Local
Clone o repositório, configure o backend e frontend, e inicie os servidores de desenvolvimento.

### Deploy Docker
Construa e execute com Docker usando docker compose up --build.

Aceda à aplicação em http://localhost:3000

---

## Guia de Instalação

### Configuração Backend

Instale dependências Python, configure a base de dados e execute o servidor Flask.

### Configuração Frontend

Instale dependências Node.js e inicie o servidor de desenvolvimento React.

### Configuração Docker

Instale Docker Desktop, construa e execute os contentores com docker compose.

---

## Guia do Utilizador

### Processo de Login

Aceda à aplicação no navegador, introduza as credenciais e utilize as contas de teste ou registe um novo utilizador.

### Registo

Registe novos utilizadores através do link de registo, introduzindo email, password e função.

### Recursos de Segurança

Proteção contra injeção SQL, validação de inputs, rate limiting, segurança CORS e hashing de passwords SHA256.

---

## Documentação API

### Endpoints de Autenticação

POST /login - Autentica credenciais do utilizador.
POST /register - Regista nova conta de utilizador.
GET /guest - Fornece acesso de convidado sem autenticação.
GET /health - Endpoint de verificação de saúde.

Todos os endpoints incluem proteção CORS, validação de inputs, prevenção de injeção SQL e rate limiting.

---

## Guia de Desenvolvimento

### Estrutura do Projeto

O projeto está organizado com backend Python Flask, frontend React, workflows GitHub Actions, configuração Docker e documentação abrangente.

### Testes

Execute testes backend com Python, testes frontend com npm, e testes de segurança específicos.

### Padrões de Código

Siga guia de estilo PEP 8 para Python, configuração ESLint para JavaScript, comentários em português e diretrizes OWASP para segurança.

---

## Guia de Deploy

### Deploy Docker

Execute docker compose up --build para desenvolvimento e docker compose -f docker-compose.prod.yml up -d para produção.

### GitHub Actions

Pipeline CI com triggers, testes, build e scanning de segurança. Pipeline de deploy com build de imagens, deploy para staging e testes de smoke.

### Variáveis de Ambiente

Configure ficheiro .env com credenciais Docker, webhook Slack e outras configurações necessárias.

### Monitorização

Verificações de saúde para backend, frontend e contentores Docker. Logging de eventos da aplicação, eventos de segurança e métricas de performance.

---

## Troubleshooting

### Issues Comuns

Redefina ambiente Docker com docker compose down -rmi all e docker system prune -a. Reinicie a base de dados removendo ficheiro users.db. Verifique conflitos de portas com netstat.

### Modo Debug

Ative modo debug no backend com FLASK_ENV=development e no frontend com npm start --verbose.

---

## Contribuição

### Workflow de Desenvolvimento

Crie branch de funcionalidade, faça alterações seguindo padrões de código, adicione testes e atualize documentação. Submeta pull request com resultados de testes.

### Processo de Review de Código

Verificações automáticas do GitHub Actions CI, scanning de segurança e verificações de qualidade de código. Review manual de conformidade de estilo, boas práticas de segurança e atualizações de documentação.

---

## Segurança

### Proteções Implementadas

Injeção SQL com queries parametrizadas, proteção XSS com sanitização de inputs, proteção CSRF com configuração CORS, rate limiting baseado em IP e segurança de passwords com hashing SHA256.

### Testes de Segurança

Execute testes de segurança com Python, teste proteção contra injeção SQL com múltiplas tentativas de login e verifique rate limiting.

### Scanning de Vulnerabilidades

Utilize Trivy para scanning de contentores, OWASP ZAP para testes de segurança web e Bandit para linting de segurança Python.

---

## Changelog

### Versão 1.0.0
Lançamento inicial com funcionalidade básica de login, integração de base de dados SQLite e funcionalidades de segurança implementadas.

### Versão 1.1.0
Contentorização Docker, GitHub Actions CI/CD, testes de segurança melhorados e controlo de acesso baseado em roles.

### Versão 1.2.0
Automação DevOps, deploy de produção, monitorização e logging, e otimizações de performance.
