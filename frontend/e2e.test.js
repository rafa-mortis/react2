const { test, expect } = require('@playwright/test');

test('basic login flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  await page.fill('#email', 'test@gmail.com');
  await page.fill('#password', '123');
  await page.click('button[type="submit"]');
  
  await expect(page.locator('h1')).toHaveText('Bem vindo!');
});
