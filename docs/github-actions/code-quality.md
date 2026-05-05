# Verificação de Qualidade de Código

Este documento descreve as verificações de qualidade de código implementadas no workflow GitHub Actions.

## Propósito

O workflow de qualidade de código garante que todo o código cumpre os standards estabelecidos para:
- Formatação e estilo de código
- Complexidade e manutenibilidade do código
- Boas práticas de segurança
- Gestão de dependências

## Triggers do Workflow

- **Push para branches**: `main`, `feature/*`
- **Pull requests**: Direcionados para `main`
- **Execução manual**: Sob demanda

## Verificações de Qualidade

### Backend (Python) - Verificações de Qualidade

#### 1. Formatação de Código com Black
```yaml
- name: Run Black (code formatting)
  run: |
    cd backend
    black --check --diff .
```

**Propósito**: Garante formatação consistente do código
**Configuração**: Segue o guia de estilo padrão do Black
**Falha**: Bloqueia PR se a formatação for inconsistente

#### 2. Ordenação de Imports com isort
```yaml
- name: Run isort (import sorting)
  run: |
    cd backend
    isort --check-only --diff .
```

**Propósito**: Garante ordenação consistente de imports
**Configuração**: Segue os standards de ordenação de imports PEP 8
**Falha**: Bloqueia PR se os imports não estiverem ordenados

#### 3. Linting com flake8
```yaml
- name: Run flake8 (linting)
  run: |
    cd backend
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

**Propósito**: Verifica problemas de estilo e erros potenciais
**Configuração**: 
- Erros críticos: E9, F63, F7, F82 (bloqueantes)
- Avisos de estilo: Complexidade máxima 10, comprimento máximo de linha 127
**Falha**: Erros críticos bloqueiam PR, avisos são reportados

#### 4. Análise de Código com pylint
```yaml
- name: Run pylint (code analysis)
  run: |
    cd backend
    pylint app.py database.py || true  # Não falha o build, apenas reporta
```

**Propósito**: Análise abrangente da qualidade do código
**Configuração**: Configuração padrão do pylint
**Falha**: Reporta issues mas não bloqueia PR

### Frontend (JavaScript/React) - Verificações de Qualidade

#### 1. ESLint (se configurado)
```yaml
- name: Run ESLint (if configured)
  run: |
    cd frontend
    npx eslint src/ --max-warnings=0 || true  # Não falha se ESLint não configurado
```

**Propósito**: Linting de código JavaScript/React
**Configuração**: Configuração ESLint específica do projeto
**Falha**: Reporta issues mas não bloqueia PR

#### 2. Análise de Dependências
```yaml
- name: Check for unused dependencies
  run: |
    cd frontend
    npx depcheck || true
```

**Propósito**: Identifica dependências não utilizadas
**Configuração**: Configurações padrão do depcheck
**Falha**: Reporta dependências não utilizadas

#### 3. Auditoria de Segurança
```yaml
- name: Audit npm packages
  run: |
    cd frontend
    npm audit --audit-level=moderate
```

**Propósito**: Verifica vulnerabilidades conhecidas em pacotes npm
**Configuração**: Limite de vulnerabilidade moderada
**Falha**: Vulnerabilidades moderadas e altas bloqueiam PR

### Verificações de Segurança

#### 1. Bandit (Scanner de Segurança Python)
```yaml
- name: Run Bandit (Python security scanner)
  uses: securecodewarrior/github-action-bandit-scan@v1
  with:
    path: backend/
```

**Propósito**: Identifica issues de segurança em código Python
**Configuração**: Configuração padrão do Bandit
**Falha**: Issues de segurança de alta e média severidade são reportados

#### 2. njsscan (Scanner de Segurança Node.js)
```yaml
- name: Run njsscan (Node.js security scanner)
  uses: securecodewarrior/github-action-njsscan@v1
  with:
    path: frontend/
```

**Propósito**: Identifica issues de segurança em código Node.js
**Configuração**: Configuração padrão do njsscan
**Falha**: Issues de segurança são reportados

#### 3. Semgrep (Scanner Multi-linguagem)
```yaml
- name: Run semgrep (multi-language security)
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/security-audit
      p/secrets
      p/owasp-top-ten
```

**Propósito**: Verificação de segurança abrangente em múltiplas linguagens
**Configuração**: OWASP Top 10, auditoria de segurança, deteção de secrets
**Falha**: Descobertas de segurança são reportadas

## Métricas de Qualidade

### Standards de Qualidade de Código

| Métrica | Alvo | Ferramenta |
|---------|--------|-----------|
| Complexidade de Código | ≤ 10 | pylint |
| Comprimento de Linha | ≤ 127 chars | flake8 |
| Cobertura de Testes | ≥ 80% | pytest |
| Issues de Segurança | 0 críticos | Bandit/njsscan |
| Vulnerabilidades | 0 moderadas/altas | npm audit |

### Portões de Qualidade

- **Issues Bloqueantes**: Devem ser corrigidos antes do merge
  - Formatação de código (Black, isort)
  - Erros de linting críticos (flake8 E9, F63, F7, F82)
  - Vulnerabilidades de segurança moderadas/altas

- **Issues de Aviso**: Devem ser revistos
  - Avisos de estilo (flake8)
  - Avisos de complexidade de código
  - Issues de segurança baixos

## Setup de Desenvolvimento Local

### Ferramentas de Qualidade Backend

```bash
# Instalar ferramentas de qualidade
pip install black isort flake8 pylint bandit

# Executar formatação
black .
isort .

# Executar linting
flake8 .
pylint app.py

# Executar scan de segurança
bandit -r .
```

### Ferramentas de Qualidade Frontend

```bash
# Instalar ferramentas de qualidade
npm install -g eslint depcheck

# Executar linting
npx eslint src/

# Verificar dependências
npx depcheck

# Executar auditoria de segurança
npm audit
```

## Troubleshooting

### Issues Comuns

1. **Falhas de Formatação Black**
   ```bash
   # Corrigir issues de formatação
   black .
   ```

2. **Issues de Ordenação de Imports**
   ```bash
   # Corrigir ordem de imports
   isort .
   ```

3. **Erros flake8**
   ```bash
   # Verificar códigos de erro específicos
   flake8 . --select=E9,F63,F7,F82
   ```

4. **ESLint Não Encontrado**
   ```bash
   # Instalar ESLint localmente
   npm install eslint --save-dev
   ```