# Documentação do Projeto

Este diretório contém a documentação completa da aplicação React Login.

## Estrutura de Diretórios

```
docs/
├── README.md                           # Este ficheiro
├── github-actions/                     # Documentação dos workflows GitHub Actions
│   ├── ci-cd-pipeline.md             # Pipeline CI/CD
│   ├── code-quality.md               # Verificação de qualidade de código
│   ├── dependency-updates.md         # Gestão de dependências
│   ├── performance-monitoring.md     # Monitorização de performance
│   └── release-management.md        # Gestão de releases
├── docker/                           # Documentação Docker
│   ├── local-development.md          # Desenvolvimento local com Docker
│   ├── production-deployment.md      # Deploy em produção
│   └── troubleshooting.md           # Resolução de problemas Docker
├── deployment/                       # Documentação de deploy
│   ├── environments.md              # Configurações de ambiente
│   ├── monitoring.md                # Monitorização da aplicação
│   └── rollback.md                 # Procedimentos de rollback
└── security/                         # Documentação de segurança
    ├── authentication.md            # Fluxo de autenticação
    ├── data-protection.md           # Proteção de dados
    └── security-scanning.md         # Verificação de segurança
```

## Início Rápido

1. **Desenvolvimento Local**: Ver `docker/local-development.md`
2. **Pipeline CI/CD**: Ver `github-actions/ci-cd-pipeline.md`
3. **Segurança**: Ver `security/authentication.md`
4. **Deploy**: Ver `deployment/environments.md`

## Visão Geral do Projeto

Esta é uma aplicação full-stack de login em React com:
- **Frontend**: React.js com interface de autenticação
- **Backend**: API Flask com autenticação de utilizadores
- **Base de Dados**: SQLAlchemy ORM com armazenamento seguro de utilizadores
- **Contentorização**: Docker e Docker Compose
- **CI/CD**: GitHub Actions para teste e deploy automatizado
- **Segurança**: Múltiplas camadas de validação de segurança

## Funcionalidades Principais

### Autenticação
- Registo e login de utilizadores
- Controlo de acesso baseado em roles (admin/convidado/normal)
- Proteção contra injeção SQL
- Validação e sanitização de inputs

### Workflow de Desenvolvimento
- Testes automatizados (unitários, integração, segurança)
- Verificação de qualidade de código (linting, formatação)
- Gestão de dependências
- Monitorização de performance
- Releases automatizados

### Deploy
- Contentorização Docker
- Suporte para múltiplos ambientes
- Deploys automatizados
- Verificação de saúde e monitorização

## Suporte

Para questões ou problemas:
1. Consulte a documentação relevante
2. Verifique os guias de resolução de problemas
3. Consulte os Issues do GitHub
4. Contacte a equipa de desenvolvimento

---

*Última atualização: $(date)*
