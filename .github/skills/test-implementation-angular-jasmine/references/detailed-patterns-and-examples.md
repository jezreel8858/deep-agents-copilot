# Test Implementation — Angular Jasmine/Karma (Exemplos Detalhados)

## 2–3) Integration Tests (ActivatedRoute, Forms) e E2E Tests (Playwright)

### Setup com ActivatedRoute Mock

```typescript
it('deve carregar dados da rota quando ActivatedRoute muda', () => {
  const activatedRoute = TestBed.inject(ActivatedRoute);
  (activatedRoute.params as Subject<any>).next({ id: 123 });
  
  fixture.detectChanges();
  expect(component.id).toBe(123);
});
```

### Form Testing

```typescript
it('deve validar formulário quando dados inválidos', () => {
  const form = component.meuForm;
  form.get('email').setValue('invalido');
  
  expect(form.valid).toBe(false);
  expect(form.get('email').errors).toBeTruthy();
});

it('deve desabilitar submit quando form inválido', () => {
  const button = fixture.debugElement.query(By.css('[type="submit"]'));
  component.meuForm.markAllAsTouched();
  fixture.detectChanges();
  
  expect(button.nativeElement.disabled).toBe(true);
});
```

## 3) E2E Tests — Playwright

### Estrutura

```
e2e-playwright/
  [feature]/
    [cenario].spec.ts
```

### Setup Básico

```typescript
import { test, expect } from '@playwright/test';

test('deve fazer login com credenciais válidas', async ({ page }) => {
  await page.goto('http://localhost:4200/login');
  
  await page.fill('[data-testid="email"]', 'user@example.com');
  await page.fill('[data-testid="password"]', 'senha123');
  await page.click('button[type="submit"]');
  
  await page.waitForURL('/dashboard');
  expect(page.url()).toContain('/dashboard');
});
```

### Waiting Strategies

```typescript
// Preferir data-testid
await page.locator('[data-testid="button-save"]').click();

// Esperar elemento visível
await expect(page.locator('.message')).toContainText('Sucesso');

// Timeout customizado
await page.locator('.modal', { timeout: 5000 }).waitFor({ state: 'visible' });
```
