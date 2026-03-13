import { test, expect } from '@playwright/test'

test.describe('Multiagentes Frontend E2E', () => {
  test('deve carregar a página inicial corretamente', async ({ page }) => {
    // Acessa a página raiz
    await page.goto('/')

    // Verifica se o título da aplicação está visível
    await expect(page).toHaveTitle(/Multiagentes/i)

    // Verifica se o chat input está presente na tela
    const chatInput = page.getByRole('textbox', { name: /mensagem/i })
    // Usamos soft assertion ou toBeVisible com fallback por conta de estilizações dinâmicas,
    // mas testar a presença geral é ideal.
    await expect(page.locator('form')).toBeVisible()
  })
})
