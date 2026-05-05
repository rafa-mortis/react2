// Importar as bibliotecas React necessárias para o componente
import React, { useState, useEffect } from 'react';

// Componente principal da aplicação de login
function App() {
  // Estados para controlar o login, formulário e erros
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Estado para verificar se o utilizador está logado
  const [email, setEmail] = useState(''); // Estado para o email do formulário
  const [password, setPassword] = useState(''); // Estado para a password do formulário
  const [error, setError] = useState(''); // Estado para mensagens de erro
  const [user, setUser] = useState(''); // Estado para guardar o utilizador logado
  const [userRole, setUserRole] = useState('normal'); // Estado para o tipo de utilizador

  // useEffect para verificar se o utilizador já está logado ao carregar a página
  useEffect(() => {
    // Verificar se existe utilizador guardado no localStorage
    const storedUser = localStorage.getItem('user');
    const storedRole = localStorage.getItem('role');
    if (storedUser) {
      setIsLoggedIn(true);
      setUser(storedUser);
      // Definir o tipo de utilizador
      setUserRole(storedRole || 'normal');
    }
  }, []);

  // Função para validar o formato do email
  const validateEmail = (email) => {
    // Validação básica de email - verifica se tem @ e . na estrutura correta
    const atIndex = email.indexOf('@');
    const dotIndex = email.lastIndexOf('.');
    return atIndex > 0 && dotIndex > atIndex + 1 && dotIndex < email.length - 1;
  };

  // Função para lidar com o login
  const handleLogin = async (e) => {
    e.preventDefault(); // Prevenir o comportamento padrão do formulário
    setError(''); // Limpar erros anteriores

    // Validação básica do email
    if (!validateEmail(email)) {
      setError('Por favor adicione um email válido com @');
      return;
    }

    try {
      // Enviar requisição POST para o backend
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000'}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }), // Enviar email e password
      });

      const data = await response.json(); // Obter resposta do servidor

      if (data.success) {
        setIsLoggedIn(true);
        setUser(data.user);
        setUserRole(data.role || 'normal');
        localStorage.setItem('user', data.user);
        localStorage.setItem('role', data.role || 'normal');
      } else {
        // Login falhou - mostrar mensagem de erro do backend
        setError(data.message);
      }
    } catch (err) {
      // Erro de conexão com o servidor
      setError('Falha ao conectar ao servidor');
    }
  };

  // Função para fazer logout
  const handleLogout = () => {
    setIsLoggedIn(false); // Resetar estado de login
    setUser(''); // Limpar utilizador
    setUserRole('normal'); // Resetar tipo de utilizador
    setEmail(''); // Limpar email do formulário
    setPassword(''); // Limpar password do formulário
    localStorage.removeItem('user'); // Remover utilizador do localStorage
    localStorage.removeItem('role'); // Remover tipo de utilizador
  };

  // Se o utilizador estiver logado, mostrar página de sucesso
  if (isLoggedIn) {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <h1>Bem vindo!</h1>
        <p>Conseguiste fazer login com sucesso!</p>
        <p>Olá {user}!</p>
        <p>Tipo de utilizador: {userRole}</p>
        <button onClick={handleLogout} style={{ padding: '10px 20px', marginTop: '20px' }}>
          Logout
        </button>
      </div>
    );
  }

  // Se o utilizador não estiver logado mostra o formulário de login
  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Página de Login</h1>
      <form onSubmit={handleLogin} style={{ display: 'inline-block', textAlign: 'left' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="email">Email:</label><br />
          <input
            type="text"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="user@gmail.com"
            style={{ padding: '5px', width: '200px' }}
          />
        </div>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="password">Password:</label><br />
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ padding: '5px', width: '200px' }}
          />
        </div>
        {/* Mostrar mensagem de erro se existir */}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit" style={{ padding: '10px 20px' }}>
          Login
        </button>
      </form>
    </div>
  );
}

export default App;
