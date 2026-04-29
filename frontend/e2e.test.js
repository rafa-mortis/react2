// End-to-end test for complete login flow
const { test, expect } = require('@playwright/test');

test('complete login flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Fill login form
  await page.fill('#email', 'test@gmail.com');
  await page.fill('#password', 'password123');
  
  // Click login button
  await page.click('button[type="submit"]');
  
  // Verify successful login
  await expect(page.locator('h1')).toContainText('Bem vindo');
  await expect(page.locator('p')).toContainText('Olá test@gmail.com');
});
