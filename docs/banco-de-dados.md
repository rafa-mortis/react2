# Banco de Dados

## Visão Geral
Implementação de banco de dados SQLite para armazenamento de usuários.

## Estrutura
- **Database**: SQLite (users.db)
- **ORM**: SQLAlchemy para mapeamento objeto-relacional
- **Model**: User com campos email, password, role

## Modelo de Dados
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    role = Column(String(20), default='normal')
```

## Usuários Padrão
- **user@gmail.com / 123456**: Usuário normal
- **admin@gmail.com / admin123**: Administrador
- **guest@gmail.com / guest123**: Convidado

## Operações
- **CREATE**: Inserção de novos usuários
- **READ**: Consulta de usuários por email
- **UPDATE**: Atualização de dados do usuário
- **DELETE**: Remoção de usuários

## Configuração
- Engine configurado para SQLite
- Sessões gerenciadas automaticamente
- Auto-creation de tabelas no startup

## Segurança
- Senhas hasheadas com SHA256
- Validação de email único
- Proteção contra SQL injection

## Volume Docker
- Mapeamento: ./backend/users.db:/app/users.db
- Persistência de dados entre reinícios
- Backup automático recomendado
