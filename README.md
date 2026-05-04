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

# Manutencao

# Atualizacao de Dependencias
- Backend: pip install --upgrade -r requirements.txt
- Frontend: npm update

# Monitorizacao
- Logs do servidor Flask mostram operacoes da base de dados
- Testes de seguranca podem ser executados regularmente
- Rate limiting ajuda a prevenir abusos