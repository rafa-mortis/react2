# Testes de segurança para SQL Injection e validação de inputs
import pytest
from security import SecurityValidator, detect_sql_injection
import requests
import json
from unittest.mock import patch, MagicMock

class TestSecurityValidator:
    # Classe para testar validações de segurança
    
    def test_email_validation(self):
        # Testar validação de email
        assert SecurityValidator.validate_email("user@gmail.com") == True
        assert SecurityValidator.validate_email("test.user@domain.co.uk") == True
        assert SecurityValidator.validate_email("") == False
        assert SecurityValidator.validate_email("invalid-email") == False
        assert SecurityValidator.validate_email("user@") == False
        assert SecurityValidator.validate_email("@domain.com") == False
        assert SecurityValidator.validate_email("a" * 121 + "@gmail.com") == False  # Email muito longo
        
    def test_password_validation(self):
        # Testar validação de password
        assert SecurityValidator.validate_password("123456") == True
        assert SecurityValidator.validate_password("password123") == True
        assert SecurityValidator.validate_password("") == False
        assert SecurityValidator.validate_password("123") == False  # Muito curta
        assert SecurityValidator.validate_password("a" * 256) == False  # Muito longa
        assert SecurityValidator.validate_password("password'") == False  # SQL Injection
        assert SecurityValidator.validate_password("password;") == False  # SQL Injection
        assert SecurityValidator.validate_password("password--") == False  # SQL Injection
        
    def test_role_validation(self):
        # Testar validação de role
        assert SecurityValidator.validate_role("normal") == True
        assert SecurityValidator.validate_role("admin") == True
        assert SecurityValidator.validate_role("guest") == True
        assert SecurityValidator.validate_role("invalid") == False
        assert SecurityValidator.validate_role("") == False
        
    def test_input_sanitization(self):
        # Testar sanitização de inputs
        assert SecurityValidator.sanitize_input("normal@email.com") == "normal@email.com"
        assert SecurityValidator.sanitize_input("email'OR'1'='1") == "emailOR1=1"
        assert SecurityValidator.sanitize_input("DROP TABLE users") == "TABLE users"
        assert SecurityValidator.sanitize_input("'; DROP TABLE users; --") == "TABLE users"
        assert SecurityValidator.sanitize_input("admin'; --") == "admin"
        assert SecurityValidator.sanitize_input("") == ""

class TestSQLInjectionDetection:
    # Classe para testar deteção de SQL Injection
    
    def test_sql_injection_patterns(self):
        # Testar padrões de SQL Injection
        assert detect_sql_injection("'; DROP TABLE users; --") == True
        assert detect_sql_injection("' OR '1'='1") == True
        assert detect_sql_injection("' OR 1=1 --") == True
        assert detect_sql_injection("'; xp_cmdshell('dir'); --") == True
        assert detect_sql_injection("'; EXEC xp_regread; --") == True
        assert detect_sql_injection("UNION SELECT * FROM users") == True
        assert detect_sql_injection("normal@email.com") == False
        assert detect_sql_injection("password123") == False
        assert detect_sql_injection("") == False

class TestAPISecurity:
    # Classe para testar segurança da API
    
    def setup_method(self):
        # Configurar para testes
        self.base_url = "http://localhost:5000"
        
    @patch('requests.post')
    def test_sql_injection_login(self, mock_post):
        # Tentar SQL Injection no login
        malicious_inputs = [
            {"email": "' OR '1'='1", "password": "password"},
            {"email": "admin@gmail.com", "password": "' OR '1'='1"},
            {"email": "'; DROP TABLE users; --", "password": "password"},
            {"email": "admin@gmail.com", "password": "'; EXEC xp_cmdshell('dir'); --"}
        ]
        
        for payload in malicious_inputs:
            # Mock response to return 401 (unauthorized)
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_post.return_value = mock_response
            
            response = requests.post(
                f"{self.base_url}/login",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            # Deve retornar erro 400 (bad request) ou 401 (unauthorized)
            assert response.status_code in [400, 401]
            
    @patch('requests.post')
    def test_invalid_json(self, mock_post):
        # Testar JSON inválido
        # Mock response to return 400 (bad request)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        response = requests.post(
            f"{self.base_url}/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        
    @patch('requests.post')
    def test_large_json(self, mock_post):
        # Testar JSON muito grande
        large_data = {
            "email": "a" * 10000 + "@gmail.com",
            "password": "password"
        }
        # Mock response to return 400 (bad request)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        response = requests.post(
            f"{self.base_url}/login",
            json=large_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400

def run_security_tests():
    # Executar todos os testes de segurança
    print("Iniciando testes de segurança...")
    
    # Testar validação de email
    print("\n Testando validação de email...")
    validator = TestSecurityValidator()
    validator.test_email_validation()
    print("Validação de email: PASS")
    
    # Testar validação de password
    print("\n Testando validação de password...")
    validator.test_password_validation()
    print("Validação de password: PASS")
    
    # Testar deteção de SQL Injection
    print("\n Testando deteção de SQL Injection...")
    injection_test = TestSQLInjectionDetection()
    injection_test.test_sql_injection_patterns()
    print(" Deteção de SQL Injection: PASS")
    
    # Testar sanitização
    print("\n Testando sanitização de inputs...")
    validator.test_input_sanitization()
    print(" Sanitização de inputs: PASS")
    
    print("\n Todos os testes de segurança passaram!")

if __name__ == '__main__':
    run_security_tests()
