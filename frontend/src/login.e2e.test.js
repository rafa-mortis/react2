// Importar as bibliotecas necessárias para o teste end-to-end
const { test, expect } = require('@playwright/test');

// Teste end-to-end: fluxo completo de login
test('basic login flow', async ({ page }) => {
  // Mock da rota de login para retornar resposta controlada
  await page.route('**/login', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, user: 'test@gmail.com', role: 'normal' }),
    });
  });
  
  // Navegar para a página de login
  await page.goto('http://localhost:3000');
  
  // Preencher o campo de email
  await page.fill('#email', 'test@gmail.com');
  // Preencher o campo de password
  await page.fill('#password', '123');
  // Clicar no botão de login
  await page.click('button[type="submit"]');
  
  // Verificar se a página de sucesso é mostrada com o texto "Bem vindo!"
  await expect(page.locator('h1')).toHaveText('Bem vindo!');
});

// Teste mock e2e: simular resposta do servidor
test('mock e2e server response', async ({ page }) => {
  // Mock da rota de login para retornar resposta controlada
  await page.route('**/login', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, user: 'mock@gmail.com' }),
    });
  });
  
  await page.goto('http://localhost:3000');
  await page.fill('#email', 'mock@gmail.com');
  await page.fill('#password', 'mock123');
  await page.click('button[type="submit"]');
  
  // Verificar se o mock funcionou
  await expect(page.locator('h1')).toHaveText('Bem vindo!');
});

// Teste mock e2e: simular erro do servidor
test('mock e2e server error', async ({ page }) => {
  // Mock da rota de login para retornar erro
  await page.route('**/login', (route) => {
    route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ success: false, message: 'Credenciais inválidas' }),
    });
  });
  
  await page.goto('http://localhost:3000');
  await page.fill('#email', 'error@gmail.com');
  await page.fill('#password', 'wrong');
  await page.click('button[type="submit"]');
  
  // Verificar se permanece na página de login (erro)
  await expect(page.locator('h1')).toHaveText('Página de Login');
});
