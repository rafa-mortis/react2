// Importar as bibliotecas necessárias para o teste end-to-end
const { test, expect } = require('@playwright/test');

// Teste end-to-end: fluxo completo de login
test('basic login flow', async ({ page }) => {
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
