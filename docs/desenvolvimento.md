# Desenvolvimento

## Visão Geral
Processo de desenvolvimento da aplicação React login com DevOps.

## Estrutura do Projeto
```
react/
├── frontend/          # Aplicação React
│   ├── src/
│   │   └── App.js     # Componente principal
│   ├── Dockerfile     # Container frontend
│   └── package.json   # Dependências
├── backend/           # API Flask
│   ├── app.py         # Aplicação principal
│   ├── database.py    # Configuração DB
│   ├── models.py      # Modelos de dados
│   └── Dockerfile     # Container backend
├── .github/           # GitHub Actions
│   └── workflows/     # Pipelines CI/CD
├── docs/              # Documentação
└── docker-compose.yml # Orquestração
```

## Tecnologias
- **Frontend**: React 18, Node.js 18
- **Backend**: Python 3.13, Flask, SQLAlchemy
- **Database**: SQLite
- **Containerização**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Security**: Trivy, CORS, Rate Limiting

## Fluxo de Desenvolvimento
1. **Setup**: Configuração ambiente local
2. **Development**: Desenvolvimento de features
3. **Testing**: Testes automatizados
4. **Containerization**: Build Docker images
5. **CI/CD**: GitHub Actions automation
6. **Deploy**: Deploy automatizado

## Comandos Úteis
```bash
# Desenvolvimento local
cd frontend && npm start
cd backend && python app.py

# Docker
docker compose up --build
docker compose down

# Testes
cd backend && python -m pytest
cd frontend && npm test
```

## Melhores Práticas
- Code review obrigatório
- Testes automatizados
- Documentação atualizada
- Security scanning regular
- Versionamento semântico

## Contribuição
- Fork do projeto
- Branch feature/nome-da-feature
- Pull request com descrição
- Code review e merge
