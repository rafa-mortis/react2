# Módulo de segurança para proteção contra SQL Injection e validação de inputs
import re
from typing import Optional
from flask import request, jsonify

class SecurityValidator:
    # Classe para validação de segurança e prevenção de SQL Injection
    
    @staticmethod
    def validate_email(email: str) -> bool:
        # Validar formato do email com regex seguro
        if not email or len(email) > 120:
            return False
        
        # Regex para validação de email (prevenção contra caracteres perigosos)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        # Validar password (comprimento mínimo e máximo)
        if not password:
            return False
        
        # Comprimento entre 6 e 255 caracteres
        if len(password) < 6 or len(password) > 255:
            return False
        
        # Prevenir caracteres perigosos (SQL Injection)
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            if char in password.lower():
                return False
        
        return True
    
    @staticmethod
    def validate_role(role: str) -> bool:
        # Validar role (apenas valores permitidos)
        valid_roles = ['normal', 'admin', 'guest']
        return role in valid_roles
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        # Sanitizar input para remover caracteres perigosos
        if not input_str:
            return ""
        
        # Remover caracteres perigosos para SQL Injection
        dangerous_patterns = [
            r"'", r'"', r';', r'--', r'/\*', r'\*/', 
            r'xp_', r'sp_', r'drop', r'delete', r'insert',
            r'update', r'exec', r'union', r'select'
        ]
        
        sanitized = input_str
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_json_request() -> tuple[bool, Optional[dict]]:
        # Validar requisição JSON e prevenir ataques
        try:
            data = request.get_json()
            if not data:
                return False, {"message": "JSON inválido"}
            
            # Limitar tamanho do JSON
            if len(str(data)) > 10000:  # 10KB limit
                return False, {"message": "JSON demasiado grande"}
            
            return True, data
        except Exception:
            return False, {"message": "Erro ao processar JSON"}

# Função para verificar SQL Injection attempts
def detect_sql_injection(input_str: str) -> bool:
    # Detetar padrões de SQL Injection
    sql_injection_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"('(\s*OR\s*|AND\s*)'[^']+'\s*=\s*'[^']+')",
        r"('(\s*OR\s*|AND\s*)\d+\s*=\s*\d+)",
        r"('\s*OR\s*'[^']+'\s*=\s*'[^']+)",
        r"('\s*OR\s*\d+\s*=\s*\d+)",
        r"(--|#|/\*|\*/)",
        r"(\bxp_\w+\b)",
        r"(\bsp_\w+\b)",
        r"(\bwaitfor\s+delay\b)",
        r"(\bconvert\s*\()",
        r"(\bcast\s*\()"
    ]
    
    for pattern in sql_injection_patterns:
        if re.search(pattern, input_str, re.IGNORECASE):
            return True
    
    return False

# Middleware de segurança para Flask
def security_middleware():
    # Verificar headers de segurança
    if request.method == 'POST':
        # Verificar Content-Type
        if not request.is_json:
            return False, {"message": "Content-Type deve ser application/json"}
        
        # Verificar User-Agent (básico)
        if not request.headers.get('User-Agent'):
            return False, {"message": "User-Agent é obrigatório"}
    
    return True, None
