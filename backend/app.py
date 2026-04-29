# Importar as bibliotecas necessárias para a aplicação Flask
from flask import Flask, request, jsonify
from flask_cors import CORS

# Criar a aplicação Flask
app = Flask(__name__)
# Habilitar CORS para permitir requisições do frontend
CORS(app)

# Rota para o endpoint de login
@app.route('/login', methods=['POST'])
def login():
    # Obter os dados JSON da requisição
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Autenticação básica para aceitar qualquer email e password não vazios
    if email and password:
        # Login bem sucedido e retorna sucesso e dados do utilizador
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': email
        }), 200
    else:
        # Login falhou e retornar erro
        return jsonify({
            'success': False,
            'message': 'Credenciais inválidas'
        }), 401

# Rota para verificação de saúde do servidor e aceita requisições GET
@app.route('/health', methods=['GET'])
def health():
    # Retornar status ok para indicar que o servidor está a funcionar
    return jsonify({'status': 'ok'}), 200

# Iniciar a aplicação Flask se o ficheiro for executado diretamente
if __name__ == '__main__':
    app.run(debug=True, port=5000)
