from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Basic authentication - accept any non-empty email/password
    if email and password:
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': email
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Credenciais inválidas'
        }), 401

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
