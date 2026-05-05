# Pipeline CI/CD

Este documento descreve o pipeline CI/CD completo para a aplicação React Login.

## Arquitetura do Pipeline

O pipeline CI/CD consiste em múltiplos workflows que correm em diferentes triggers:

### Workflows Principais

1. **Pipeline CI** (`.github/workflows/ci.yml`)
   - Triggers: Push para `main/devops`, PR para `main`
   - Executa: Testes backend, testes frontend, testes Docker, scans de segurança

2. **Deploy para Produção** (`.github/workflows/deploy.yml`)
   - Triggers: Push para `main`, Manual
   - Executa: Build/push Docker, deploy staging, testes de smoke

3. **Qualidade de Código** (`.github/workflows/code-quality.yml`)
   - Triggers: Push para `main/feature/*`, PR para `main`
   - Executa: Linting, formatação, análise de segurança

4. **Atualizações de Dependências** (`.github/workflows/dependency-update.yml`)
   - Triggers: Schedule semanal, Manual
   - Executa: Atualizações de dependências, scans de segurança, criação de PR

5. **Monitorização de Performance** (`.github/workflows/performance-monitoring.yml`)
   - Triggers: Push para `main`, PR para `main`, Schedule diário
   - Executa: Testes de performance, análise de bundle, benchmarks da base de dados

6. **Gestão de Releases** (`.github/workflows/release-management.yml`)
   - Triggers: Tags Git, Manual
   - Executa: Criação de release, build de imagens, deploy de produção

## Fluxo do Pipeline

### 1. Integração Contínua (CI)

**Objetivo**: Garantir qualidade e funcionalidade do código
**Triggers**: Cada push e pull request

**Jobs**:
- **Testes Backend**: Testes unitários Python, testes de segurança, testes da base de dados
- **Testes Frontend**: Testes unitários React, testes de integração
- **Build Docker**: Verifica se as imagens Docker build corretamente
- **Scan de Segurança**: Verificação de vulnerabilidades com Trivy

### 2. Deploy Contínuo (CD)

**Objetivo**: Deploy de código validado para produção
**Triggers**: CI bem-sucedido na branch main

**Jobs**:
- **Build e Deploy**: Build e push de imagens Docker
- **Deploy Staging**: Deploy para ambiente de staging
- **Testes de Smoke**: Validação do deploy
- **Notificação**: Notificações Slack

### 3. Qualidade de Código

**Objetivo**: Manter standards de código e segurança
**Triggers**: Todos os pushes e PRs

**Jobs**:
- **Qualidade Backend**: Black, isort, flake8, pylint
- **Qualidade Frontend**: ESLint, verificação de dependências, audit npm
- **Segurança**: Bandit, njsscan, semgrep

## Configuração

### Secrets Necessários

| Secret | Propósito | Necessário Para |
|---------|-----------|----------------|
| `DOCKER_USERNAME` | Utilizador Docker Hub | Deploy, Release |
| `DOCKER_PASSWORD` | Password Docker Hub | Deploy, Release |
| `SLACK_WEBHOOK` | Webhook Slack | Deploy, Release |
| `SNYK_TOKEN` | Token Snyk | Atualizações de Dependências |
| `GITHUB_TOKEN` | Acesso API GitHub | Todos os workflows |

### Variáveis de Ambiente

| Variável | Propósito | Default |
|-----------|-----------|---------|
| `PYTHON_VERSION` | Versão Python | `3.13` |
| `NODE_VERSION` | Versão Node.js | `18` |
| `DOCKER_REGISTRY` | Registry Docker | `docker.io` |

## Monitorização e Alertas

### Critérios de Sucesso

- **Pipeline CI**: Todos os testes passam, scan de segurança limpo
- **Deploy**: Imagens push, deploy bem-sucedido
- **Qualidade**: Formatação de código passa, sem issues críticos
- **Performance**: Scores Lighthouse > 80, tamanho de bundle dentro dos limites

### Gestão de Falhas

- **Falhas de Teste**: Pipeline para, notificação enviada
- **Issues de Segurança**: Pipeline falha, relatório detalhado gerado
- **Regressão de Performance**: Comentário no PR com comparação de benchmarks
- **Falhas de Deploy**: Rollback iniciado, alerta enviado

## Troubleshooting

### Issues Comuns

1. **Falhas de Build Docker**
   - Verifique sintaxe do Dockerfile
   - Verifique se as imagens base estão acessíveis
   - Reveja os logs de build

2. **Falhas de Teste**
   - Verifique dependências de teste
   - Verifique setup do ambiente de teste
   - Reveja os logs de teste

3. **Falhas de Scan de Segurança**
   - Atualize dependências vulneráveis
   - Reveja relatórios de scan de segurança
   - Enderece vulnerabilidades de alta prioridade