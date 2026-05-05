# Importar as bibliotecas necessárias para a aplicação Flask
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from database import get_db, engine
from models import User
from sqlalchemy import select, text
from security import SecurityValidator, detect_sql_injection, security_middleware
import hashlib
import time

# Criar a aplicação Flask
app = Flask(__name__)
# Configurar CORS com segurança restrita
CORS(app, 
     origins=['http://localhost:3000'],  # Apenas permitir frontend local
     methods=['GET', 'POST'],  # Apenas métodos necessários
     allow_headers=['Content-Type', 'Authorization'],  # Headers permitidos
     supports_credentials=True,
     max_age=3600  # Cache por 1 hora
)

# Rota para o endpoint de login com base de dados e segurança
@app.route('/login', methods=['POST'])
def login():
    # Middleware de segurança
    is_valid, error_msg = security_middleware()
    if not is_valid:
        return jsonify({'success': False, 'message': error_msg['message']}), 400
    
    # Validar requisição JSON
    is_valid, data = SecurityValidator.validate_json_request()
    if not is_valid:
        return jsonify(data), 400
    
    # Obter e validar dados
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    # Verificar SQL Injection
    if detect_sql_injection(email) or detect_sql_injection(password):
        return jsonify({'success': False, 'message': 'Input inválido detectado'}), 400
    
    # Validar formato dos dados
    if not SecurityValidator.validate_email(email):
        return jsonify({'success': False, 'message': 'Email inválido'}), 400
    
    if not SecurityValidator.validate_password(password):
        return jsonify({'success': False, 'message': 'Password inválida'}), 400
    
    # Sanitizar inputs
    email = SecurityValidator.sanitize_input(email)
    password = SecurityValidator.sanitize_input(password)
    
    # Autenticação com base de dados (usando query parametrizada)
    db = next(get_db())
    try:
        # Query segura com ORM para prevenir SQL Injection
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
        
        if user and user.password == hashlib.sha256(password.encode()).hexdigest():
            # Login bem sucedido - utilizador encontrado e password correta
            user_role = getattr(user, 'role', 'normal')
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': email,
                'role': user_role
            }), 200
        else:
            # Login falhou - password incorreta
            return jsonify({
                'success': False,
                'message': 'Credenciais inválidas'
            }), 401
    except Exception as e:
        # Erro na base de dados
        print(f"Erro detalhado: {str(e)}")  # Debug logging
        return jsonify({
            'success': False,
            'message': 'Erro na autenticação',
            'error': str(e)  # Include error in response for debugging
        }), 500
    finally:
        db.close()

# Rota para acesso de visitante (guest)
@app.route('/guest', methods=['GET'])
def guest_access():
    # Retornar dados de visitante sem autenticação
    return jsonify({
        'success': True,
        'message': 'Acesso de visitante permitido',
        'user': 'guest',
        'role': 'guest'
    }), 200

# Rota para verificação de saúde do servidor e aceita requisições GET
@app.route('/health', methods=['GET'])
def health():
    # Retornar status ok para indicar que o servidor está a funcionar
    return jsonify({'status': 'ok'}), 200

# Rota para registo de novos utilizadores
@app.route('/register', methods=['POST'])
def register():
    # Obter os dados JSON da requisição
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'normal')  # Default role é 'normal'
    
    # Verificar se os dados foram fornecidos
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Email e password são obrigatórios'
        }), 400
    
    db = next(get_db())
    try:
        # Verificar se o utilizador já existe
        existing_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email já registado'
            }), 409
        
        # Criar novo utilizador com role especificado
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
        # Erro na base de dados
        return jsonify({
            'success': False,
            'message': 'Erro ao registar utilizador'
        }), 500
    finally:
        db.close()

# Rota para criar utilizador admin
@app.route('/admin/create', methods=['POST'])
def create_admin():
    # Obter os dados JSON da requisição
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Verificar se os dados foram fornecidos
    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Email e password são obrigatórios'
        }), 400
    
    db = next(get_db())
    try:
        # Verificar se o utilizador já existe
        existing_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email já registado'
            }), 409
        
        # Criar utilizador admin
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        admin_user = User(email=email, password=hashed_password, role='admin')
        db.add(admin_user)
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Administrador criado com sucesso',
            'user': email,
            'role': 'admin'
        }), 201
    except Exception as e:
        # Erro na base de dados
        return jsonify({
            'success': False,
            'message': 'Erro ao criar administrador'
        }), 500
    finally:
        db.close()

# Iniciar a aplicação Flask se o ficheiro for executado diretamente
if __name__ == '__main__':
    # Criar tabelas na base de dados
    from database import Base
    Base.metadata.create_all(bind=engine)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
