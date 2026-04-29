// Importar as bibliotecas necessárias para o teste de integração
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Teste de integração: verificar se a página de login é renderizada corretamente
test('renders login page', () => {
  render(<App />);

  // Verificar se o título da página de login está presente
  expect(screen.getByText(/Página de Login/i)).toBeInTheDocument();
  // Verificar se o campo de email está presente
  expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
  // Verificar se o campo de password está presente
  expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
});