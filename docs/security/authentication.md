# Segurança de Autenticação

Este documento descreve a implementação de segurança de autenticação para a aplicação React Login.

## Propósito

A segurança de autenticação garante:
- Autenticação segura de utilizadores
- Proteção contra ataques comuns
- Gestão adequada de sessões
- Controlo de acesso baseado em roles

## Fluxo de Autenticação

### 1. Registo de Utilizador

#### Processo de Registo
```python
# backend/app.py - Endpoint de registo
@app.route('/register', methods=['POST'])
def register():
    # Obter e validar dados
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'normal')
    
    # Validação de input
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Email e password são obrigatórios'
        }), 400
    
    # Verificar se utilizador existe
    db = next(get_db())
    try:
        existing_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email já registado'
            }), 409
        
        # Criar novo utilizador com password hashed
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(email=email, password=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Utilizador registado com sucesso',
            'user': email,
            'role': role
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erro ao registar utilizador'
        }), 500
    finally:
        db.close()
```

#### Frontend de Registo
```javascript
// frontend/src/components/Register.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    role: 'normal'
  });
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email é inválido';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password é obrigatória';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password deve ter pelo menos 8 caracteres';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords não correspondem';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          role: formData.role
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        navigate('/login');
      } else {
        setErrors({ submit: data.message });
      }
    } catch (error) {
      setErrors({ submit: 'Registo falhou. Tente novamente.' });
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Campos do formulário com validação */}
    </form>
  );
};
```

### 2. Login de Utilizador

#### Processo de Login
```python
# backend/app.py - Endpoint de login
@app.route('/login', methods=['POST'])
def login():
    # Middleware de segurança
    is_valid, error_msg = security_middleware()
    if not is_valid:
        return jsonify({'success': False, 'message': error_msg['message']}), 400
    
    # Validar pedido
    is_valid, data = SecurityValidator.validate_json_request()
    if not is_valid:
        return jsonify(data), 400
    
    # Obter e validar dados
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    # Proteção contra injeção SQL
    if detect_sql_injection(email) or detect_sql_injection(password):
        return jsonify({'success': False, 'message': 'Input inválido detetado'}), 400
    
    # Validação de email
    if not SecurityValidator.validate_email(email):
        return jsonify({'success': False, 'message': 'Email inválido'}), 400
    
    # Validação de password
    if not SecurityValidator.validate_password(password):
        return jsonify({'success': False, 'message': 'Password inválida'}), 400
    
    # Sanitizar inputs
    email = SecurityValidator.sanitize_input(email)
    password = SecurityValidator.sanitize_input(password)
    
    # Autenticação com base de dados
    db = next(get_db())
    try:
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
        
        if user and user.password == hashlib.sha256(password.encode()).hexdigest():
            # Login bem sucedido
            return jsonify({
                'success': True,
                'message': 'Login bem sucedido',
                'user': email,
                'role': getattr(user, 'role', 'normal')
            }), 200
        else:
            # Login falhou
            return jsonify({
                'success': False,
                'message': 'Credenciais inválidas'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erro na autenticação'
        }), 500
    finally:
        db.close()
```

## Medidas de Segurança

### 1. Validação de Input

#### Validador de Segurança
```python
# backend/security.py
import re
import html
from typing import Tuple, Dict, Any

class SecurityValidator:
    @staticmethod
    def validate_json_request() -> Tuple[bool, Dict[str, Any]]:
        """Validar formato JSON do pedido"""
        try:
            data = request.get_json()
            if not data:
                return False, {'success': False, 'message': 'Formato JSON inválido'}
            return True, data
        except Exception:
            return False, {'success': False, 'message': 'Formato JSON inválido'}
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validar força da password"""
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitizar input do utilizador"""
        return html.escape(input_str.strip())
```

### 2. Proteção contra Injeção SQL

#### Detecção de Injeção SQL
```python
# backend/security.py
SQL_INJECTION_PATTERNS = [
    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
    r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
    r"(\b(OR|AND)\s+['\"][\w\s]*['\"]\s*=\s*['\"][\w\s]*['\"])",
    r"(--|#|/\*|\*/)",
    r"(\b(ASCII|CHAR|CONCAT|CONCAT_WS|GROUP_CONCAT|LENGTH|SUBSTRING|MID)\b)"
]

def detect_sql_injection(input_str: str) -> bool:
    """Detetar tentativas de injeção SQL"""
    if not input_str:
        return False
    
    input_upper = input_str.upper()
    
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, input_upper, re.IGNORECASE):
            return True
    
    return False
```

### 3. Rate Limiting

#### Middleware de Rate Limiting
```python
# backend/middleware/rate_limiter.py
from collections import defaultdict
import time
from functools import wraps

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Verificar se pedido é permitido"""
        now = time.time()
        window_start = now - window
        
        # Remover pedidos antigos
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if req_time > window_start
        ]
        
        # Verificar se limite excedido
        if len(self.requests[key]) >= limit:
            return False
        
        # Adicionar pedido atual
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(limit: int = 5, window: int = 60):
    """Decorador de rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            if not rate_limiter.is_allowed(client_ip, limit, window):
                return jsonify({
                    'success': False,
                    'message': 'Limite de tentativas excedido. Tente mais tarde.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## Segurança de Password

### 1. Hashing de Password

#### Armazenamento Seguro de Password
```python
# backend/security/password_security.py
import hashlib
import secrets
import bcrypt

class PasswordSecurity:
    @staticmethod
    def hash_password_bcrypt(password: str) -> str:
        """Hash password usando bcrypt (recomendado)"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password_bcrypt(password: str, stored_hash: str) -> bool:
        """Verificar password usando bcrypt"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def hash_password_sha256(password: str) -> str:
        """Hash password usando SHA-256 (implementação atual)"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"
```

### 2. Política de Password

#### Requisitos de Password
```python
# backend/policies/password_policy.py
PASSWORD_POLICY = {
    'min_length': 8,
    'max_length': 128,
    'require_uppercase': True,
    'require_lowercase': True,
    'require_digits': True,
    'require_special_chars': True,
    'forbidden_patterns': [
        r'password',
        r'123456',
        r'qwerty',
        r'admin',
        r'root'
    ],
    'history_count': 5
}

def validate_password_policy(password: str, user_history: list = None) -> dict:
    """Validar password contra política"""
    issues = []
    
    # Requisitos de comprimento
    if len(password) < PASSWORD_POLICY['min_length']:
        issues.append(f"Password deve ter pelo menos {PASSWORD_POLICY['min_length']} caracteres")
    
    # Requisitos de caracteres
    if PASSWORD_POLICY['require_uppercase'] and not re.search(r'[A-Z]', password):
        issues.append("Password deve conter pelo menos uma letra maiúscula")
    
    if PASSWORD_POLICY['require_lowercase'] and not re.search(r'[a-z]', password):
        issues.append("Password deve conter pelo menos uma letra minúscula")
    
    if PASSWORD_POLICY['require_digits'] and not re.search(r'\d', password):
        issues.append("Password deve conter pelo menos um dígito")
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues
    }
```

## Monitorização de Segurança

### 1. Eventos de Autenticação

#### Logging de Eventos de Segurança
```python
# backend/middleware/security_logging.py
import logging
from datetime import datetime

security_logger = logging.getLogger('security')

class SecurityEventLogger:
    @staticmethod
    def log_login_attempt(email: str, ip_address: str, success: bool, reason: str = None):
        """Registar tentativa de login"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'login_attempt',
            'email': email,
            'ip_address': ip_address,
            'success': success,
            'reason': reason
        }
        security_logger.info(f"LOGIN_ATTEMPT: {event}")
    
    @staticmethod
    def log_security_violation(ip_address: str, violation_type: str, details: str):
        """Registar violação de segurança"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'security_violation',
            'ip_address': ip_address,
            'violation_type': violation_type,
            'details': details
        }
        security_logger.warning(f"SECURITY_VIOLATION: {event}")
```

### 2. Proteção contra Brute Force

#### Detecção de Brute Force
```python
# backend/middleware/brute_force.py
from collections import defaultdict
import time

class BruteForceProtection:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = defaultdict(dict)
        self.max_attempts = 5
        self.block_duration = 900  # 15 minutos
        self.attempt_window = 300  # 5 minutos
    
    def record_failed_attempt(self, ip_address: str, email: str = None):
        """Registar tentativa de login falhada"""
        now = time.time()
        window_start = now - self.attempt_window
        
        # Limpar tentativas antigas
        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address]
            if attempt['timestamp'] > window_start
        ]
        
        # Adicionar nova tentativa
        self.failed_attempts[ip_address].append({
            'timestamp': now,
            'email': email
        })
        
        # Verificar se deve bloquear
        if len(self.failed_attempts[ip_address]) >= self.max_attempts:
            self.block_ip(ip_address)
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Verificar se IP está bloqueado"""
        if ip_address not in self.blocked_ips:
            return False
        
        block_info = self.blocked_ips[ip_address]
        if time.time() - block_info['blocked_at'] > self.block_duration:
            del self.blocked_ips[ip_address]
            return False
        
        return True
```

## Métricas de Autenticação

### 1. KPIs de Autenticação

#### Indicadores Chave de Performance
| Métrica | Alvo | Medição |
|---------|------|---------|
| Taxa de Sucesso de Login | > 95% | Logins bem sucedidos / Total de tentativas |
| Taxa de Sucesso de Registo | > 90% | Registos bem sucedidos / Total de tentativas |
| Tempo Médio de Login | < 2 segundos | Tempo do pedido à resposta |
| Taxa de Login Falhado | < 5% | Logins falhados / Total de tentativas |

---

*Para informação de proteção de dados, ver [data-protection.md](data-protection.md).*
