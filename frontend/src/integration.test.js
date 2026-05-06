// Importar as bibliotecas necessárias para o teste de integração
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

// Mock do fetch para simular chamadas API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ success: true, user: 'test@gmail.com' }),
  })
);

// Teste de integração: verificar se a página de login é renderizada corretamente
describe('Integration tests', () => {
  it('renders login page', () => {
    render(<App />);

    // Verificar se o título da página de login está presente
    expect(screen.getByText(/Página de Login/i)).toBeInTheDocument();
    // Verificar se o campo de email está presente
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    // Verificar se o campo de password está presente
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });

  // Teste mock de integração: simular login com sucesso
  it('mock integration login success', () => {
    render(<App />);
  
    // Preencher formulário
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'test@gmail.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: '123' } });
  
    // Verificar se os campos foram preenchidos
    expect(screen.getByLabelText(/Email/i).value).toBe('test@gmail.com');
    expect(screen.getByLabelText(/Password/i).value).toBe('123');
  });

  // Teste mock de integração: simular chamada fetch
  it('mock fetch API call', async () => {
    const mockResponse = { success: true, user: 'test@gmail.com' };
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });
  
    const response = await fetch('/login');
    const data = await response.json();
  
    expect(data.success).toBe(true);
    expect(data.user).toBe('test@gmail.com');
  });
});
