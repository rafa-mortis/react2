# Gestão de Dependências

Este documento descreve o processo de atualização de dependências para a aplicação React Login.

## Propósito

O workflow de gestão de dependências garante que:
- As dependências são mantidas atualizadas
- As vulnerabilidades de segurança são endereçadas prontamente
- As breaking changes são detetadas cedo
- O processo de atualização é automatizado e rastreado

## Triggers do Workflow

- **Schedule**: Todas as segundas às 9:00 AM UTC
- **Execução manual**: Sob demanda

## Processo de Atualização

### Dependências Python

#### 1. Processo de Atualização de Dependências
```yaml
- name: Update requirements.txt
  run: |
    cd backend
    pip-compile requirements.in --upgrade
    pip install -r requirements.txt
```

**Propósito**: Atualiza dependências Python para as versões mais recentes
**Ferramenta**: pip-compile para resolução de dependências
**Output**: requirements.txt atualizado com novas versões exatas para reprodutibilidade

#### 2. Processo de Validação
```yaml
- name: Run tests
  run: |
    cd backend
    python -m pytest testes/ -v || python testes/test_security.py && python testes/test_database.py
```

**Propósito**: Garante que as atualizações não quebram a funcionalidade
**Cobertura**: Testes de segurança e testes da base de dados
**Falha**: Bloqueia criação de PR se os testes falharem

#### 3. Criação de Pull Request
```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v5
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    commit-message: 'chore: update Python dependencies'
    title: 'Update Python Dependencies'
    branch: chore/update-python-deps
    delete-branch: true
```

**Propósito**: Criação automatizada de PR para revisão
**Branch**: Branch temporária para atualizações
**Cleanup**: Eliminação automática da branch após merge

### Dependências Node.js

#### 1. Processo de Atualização de Dependências
```yaml
- name: Update dependencies
  run: |
    cd frontend
    npm update
    npm audit fix --audit-level=moderate || true
```

**Propósito**: Atualiza dependências Node.js
**Ferramenta**: npm update para versões compatíveis mais recentes
**Segurança**: Correções automáticas para vulnerabilidades moderadas

#### 2. Processo de Validação
```yaml
- name: Run tests
  run: |
    cd frontend
    npm test -- --coverage --watchAll=false
```

**Propósito**: Garante que as atualizações não quebram a funcionalidade
**Cobertura**: Testes unitários com relatório de cobertura
**Falha**: Bloqueia criação de PR se os testes falharem

#### 3. Criação de Pull Request
```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v5
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    commit-message: 'chore: update Node.js dependencies'
    title: 'Update Node.js Dependencies'
    branch: chore/update-node-deps
    delete-branch: true
```

**Propósito**: Criação automatizada de PR para revisão
**Branch**: Branch temporária para atualizações
**Cleanup**: Eliminação automática da branch após merge

### Verificação de Segurança

#### 1. Scan de Segurança Snyk
```yaml
- name: Run Snyk security scan
  uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high frontend/
    command: monitor
```

**Propósito**: Monitorização de segurança contínua
**Limite**: Apenas issues de alta severidade
**Integração**: Dashboard Snyk para rastreamento

#### 2. Scan de Segurança Python
```yaml
- name: Run Snyk for Python
  uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high backend/
    command: monitor
```

**Propósito**: Monitorização de segurança específica para Python
**Limite**: Apenas issues de alta severidade
**Integração**: Dashboard Snyk para rastreamento

## Configuração

### Secrets Necessários

| Secret | Propósito | Necessário Para |
|--------|-----------|----------------|
| `GITHUB_TOKEN` | Acesso API GitHub | Criação de PR |
| `SNYK_TOKEN` | Acesso API Snyk | Verificação de segurança |

### Ficheiros de Dependências

#### Python (backend/)
- `requirements.in`: Especificações de dependências de origem
- `requirements.txt`: Dependências compiladas, fixadas

#### Node.js (frontend/)
- `package.json`: Especificações de dependências
- `package-lock.json`: Árvore de dependências fixada

## Estratégia de Atualização

### Política de Versões

| Tipo de Dependência | Estratégia de Atualização | Frequência |
|---------------------|----------------------------|-------------|
| Patches de segurança | Imediata | Conforme necessário |
| Atualizações menores | Semanal | Automatizada |
| Atualizações maiores | Manual | Revisão necessária |

### Avaliação de Risco

#### Atualizações de Baixo Risco
- Versões de patch (x.x.1 → x.x.2)
- Patches de segurança
- Correções de bugs

#### Atualizações de Médio Risco
- Versões menores (x.1.x → x.2.x)
- Novas funcionalidades
- Potenciais breaking changes

#### Atualizações de Alto Risco
- Versões maiores (1.x.x → 2.x.x)
- Breaking changes
- Modificações de API

## Gestão de Conflitos

### Conflitos de Atualização

1. **Falhas de Teste**
   - Reveja os logs de teste
   - Identifique breaking changes
   - Atualize o código correspondentemente
   - Execute novamente os testes

2. **Vulnerabilidades de Segurança**
   - Priorize atualizações de segurança
   - Avalie o impacto
   - Aplique patches prontamente
   - Monitore para regressões

3. **Conflitos de Dependências**
   - Reveja a árvore de dependências
   - Resolva conflitos de versão
   - Atualize as restrições
   - Teste exaustivamente

### Intervenção Manual

#### Quando Intervir
- **Atualizações de versão maior**
- **Breaking changes**
- **Falhas de teste**
- **Atualizações críticas de segurança**

#### Passos de Intervenção
1. **Avaliar Impacto**: Reveja os logs de alteração
2. **Atualizar Código**: Enderece breaking changes
3. **Testar Exaustivamente**: Teste abrangente
4. **Deploy Cuidadoso**: Rollout em etapas

## Monitorização e Relatórios

### Métricas de Atualização

| Métrica | Alvo | Medição |
|----------|-------|----------|
| Frequência de Atualização | Semanal | Execuções automatizadas |
| Tempo de Patch de Segurança | < 24 horas | Monitorização CVE |
| Taxa de Sucesso de Teste | 100% | Testes automatizados |
| Tempo de Merge de PR | < 48 horas | Processo de revisão |

### Relatórios

#### Relatórios Automatizados
- **Resumos de PR**: PRs de atualização de dependências automatizadas
- **Relatórios de Segurança**: Relatórios de vulnerabilidades Snyk
- **Logs de Atualização**: Logs de execução GitHub Actions

#### Revisões Manuais
- **Revisão Mensal de Dependências**: Avaliação abrangente
- **Revisão Trimestral de Segurança**: Avaliação de postura de segurança
- **Planeamento Anual de Atualizações Maiores**: Atualizações estratégicas

## Setup de Desenvolvimento Local

### Gestão de Dependências Python

```bash
# Instalar pip-tools
pip install pip-tools

# Atualizar dependências
pip-compile requirements.in --upgrade

# Instalar dependências atualizadas
pip install -r requirements.txt

# Verificar issues de segurança
pip-audit
```

### Gestão de Dependências Node.js

```bash
# Verificar pacotes desatualizados
npm outdated

# Atualizar dependências
npm update

# Corrigir issues de segurança
npm audit fix

# Verificar issues de segurança
npm audit
```

## Boas Práticas

### Higiene de Dependências

1. **Atualizações Regulares**: Mantenha as dependências atualizadas
2. **Monitorização de Segurança**: Scans de segurança regulares
3. **Fixação de Versões**: Use versões exatas em produção
4. **Documentação**: Documente requisitos de dependências

### Processo de Atualização

1. **Testar Exaustivamente**: Cobertura de teste abrangente
2. **Rever Alterações**: Compreenda breaking changes
3. **Rollout em Etapas**: Deploy incremental
4. **Monitorizar de Perto**: Observe por issues

### Práticas de Segurança

1. **Scanning de Vulnerabilidades**: Scans de segurança regulares
2. **Patching Rápido**: Atualizações rápidas de segurança
3. **Revisão de Dependências**: Auditorias regulares de dependências
4. **Alertas de Segurança**: Notificações de segurança automatizadas