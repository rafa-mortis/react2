# Segurança

## Visão Geral
Implementação de segurança completa na aplicação React login.

## Proteções Implementadas
- **SQL Injection**: Proteção contra injeção SQL
- **Input Validation**: Validação e sanitização de dados
- **Rate Limiting**: Limite de requisições por IP
- **CORS Security**: Configuração segura de CORS
- **Password Hashing**: SHA256 para senhas

## User Roles
- **Normal**: Acesso básico à aplicação
- **Admin**: Acesso administrativo completo
- **Guest**: Acesso limitado de visitante

## Configuração CORS
```python
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

## Rate Limiting
- Limite: 100 requisições por minuto por IP
- Proteção contra ataques de força bruta
- Configuração automática de bloqueio

## Security Scanning
- Trivy integration em GitHub Actions
- Scan automatizado de vulnerabilidades
- Relatórios de segurança gerados automaticamente

## Melhores Práticas
- Senhas nunca armazenadas em texto claro
- Validação rigorosa de inputs
- Logs de segurança implementados
- Monitoramento de atividades suspeitas
