---
name: test-implementation-angular-vitest
description: >
  Padrões consolidados para implementação de testes em Angular 20/21+ com Vitest,
  incluindo configuração nativa (Angular 20+ via @angular/build:unit-test),
  setup com TestBed, mocking com vi.fn()/vi.spyOn(), testes zoneless,
  Signals, cobertura com @vitest/coverage-v8 e migração de Jasmine/Karma.
tier: 2
category: testing
triggers:
  - "vitest angular"
  - "angular vitest"
  - "migrar jasmine vitest"
  - "karma vitest"
  - "ng test vitest"
  - "vi.fn"
  - "vi.spyOn"
  - "angular 20 21 testes"
  - "angular vitest setup"
  - "vitest testbed"
  - "vitest zoneless"
  - "vitest signals"
  - "vitest coverage angular"
stack: "Angular 20+ + Vitest 3+ + @angular/build:unit-test + @vitest/coverage-v8"
source_docs:
  - .github/instructions/angular-v21-frontend.instructions.md
  - .github/skills/test-implementation-frontend/SKILL.md
  - .github/skills/test-coverage-governance/SKILL.md
source_docs_lazy:
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Test Implementation — Angular + Vitest

> **Escopo**: implementação específica para **Angular 20/21+ com Vitest** como test runner oficial.
> Esta skill especializa os conceitos agnósticos de arquitetura de testes frontend estabelecidos em:
> - [.github/skills/test-implementation-frontend/SKILL.md](../test-implementation-frontend/SKILL.md)
> Para padrões com Jasmine/Karma (legado), consulte `test-implementation-angular-jasmine`.

## Contexto

A partir do **Angular 20**, o suporte nativo ao Vitest foi introduzido via builder `@angular/build:unit-test`. No **Angular 21** o suporte tornou-se **estável e padrão** para novos projetos — ao rodar `ng new`, Vitest é a opção padrão e Karma/Jasmine são considerados legado.

**Vantagens da Stack Modernizada:**
- Baseado em Vite — startup ultra-rápido (HMR nativo) e watch instantâneo.
- API compatível com Jest (`describe`, `it`, `expect`, `vi.fn()`).
- `globals: true` dispensa imports de `describe`/`it`/`expect` em cada spec.
- Suporte nativo a TypeScript sem transpilação extra.
- Coverage com provider `v8` de alta performance.

---

## 1) Setup — Configuração Nativa Angular 20+

### Dependências

```bash
# Instalação mínima (happy-dom é detectado automaticamente pelo Angular CLI)
npm install -D vitest happy-dom @vitest/coverage-v8
```

### angular.json

```json
{
  "projects": {
    "[nome-projeto]": {
      "architect": {
        "test": {
          "builder": "@angular/build:unit-test",
          "options": {
            "tsConfig": "tsconfig.spec.json",
            "runner": "vitest",
            "buildTarget": "::development",
            "providersFile": "src/test-providers.ts"
          }
        }
      }
    }
  }
}
```

### src/test-providers.ts (providers globais — Angular 20+ com `providersFile`)

```typescript
import { provideZonelessChangeDetection } from '@angular/core';

// Providers disponíveis em TODOS os testes — sem repetição em cada spec
export default [
  provideZonelessChangeDetection(),
];
```

### tsconfig.spec.json

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "outDir": "./out-tsc/spec",
    "types": ["vitest/globals"]
  },
  "files": ["src/test-providers.ts"],
  "include": ["src/**/*.spec.ts", "src/**/*.d.ts"]
}
```

### vitest.config.ts (configuração estendida)

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['src/test-setup.ts'],
    include: ['src/**/*.spec.ts'],
    restoreMocks: true,                    // limpa vi.spyOn/vi.fn após cada teste
    clearMocks: true,                      // limpa mock.calls entre testes
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      reportsDirectory: 'coverage',
      thresholds: {
        statements: 80,
        branches: 70,
        functions: 80,
        lines: 80,
      },
      exclude: ['src/environments/**', '**/*.config.ts', '**/*.routes.ts'],
    },
  },
});
```

---

## 2) Unit Tests — Componentes com TestBed

### Padrão Base (Componente Standalone — Angular 21 zoneless)

```typescript
// src/app/[feature]/[nome].component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { [Nome]Component } from './[nome].component';
import { [Nome]Service } from '../services/[nome].service';

describe('[Nome]Component', () => {
  let component: [Nome]Component;
  let fixture: ComponentFixture<[Nome]Component>;
  let [nome]Service: { buscar: ReturnType<typeof vi.fn>; salvar: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    [nome]Service = {
      buscar: vi.fn().mockResolvedValue([{ id: 1, nome: 'Teste' }]),
      salvar: vi.fn().mockResolvedValue({ id: 2 }),
    };

    await TestBed.configureTestingModule({
      imports: [[Nome]Component],  // standalone
      providers: [
        { provide: [Nome]Service, useValue: [nome]Service },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent([Nome]Component);
    component = fixture.componentInstance;
  });

  it('deve carregar dados ao inicializar', async () => {
    fixture.detectChanges();
    await fixture.whenStable();  // aguarda efeitos assíncronos zoneless

    expect([nome]Service.buscar).toHaveBeenCalledOnce();
    expect(component.itens()).toHaveLength(1);  // Signal
  });

  it('deve exibir mensagem de erro quando serviço falhar', async () => {
    [nome]Service.buscar.mockRejectedValue(new Error('Falha na API'));

    fixture.detectChanges();
    await fixture.whenStable();

    expect(component.erro()).toBeTruthy();
  });
});
```

### Component Harnesses (`@angular/cdk/testing`)

Desacopla os testes da estrutura interna do DOM do componente:

```typescript
import { TestbedHarnessEnvironment } from '@angular/cdk/testing/testbed';
import { MatButtonHarness } from '@angular/material/button/testing';
import { HarnessLoader } from '@angular/cdk/testing';

it('deve disparar clique via Harness', async () => {
  const loader = TestbedHarnessEnvironment.loader(fixture);
  const botaoSalvar = await loader.getHarness(MatButtonHarness.with({ text: 'Salvar' }));

  expect(await botaoSalvar.isDisabled()).toBe(false);
  await botaoSalvar.click();
  await fixture.whenStable();
});
```

---

## 3) Mocking com Vitest — vi.fn() e vi.spyOn()

### vi.fn() vs jasmine.createSpy()

```typescript
// Vitest: mock síncrono e assíncrono
const spy = vi.fn().mockReturnValue(dados);           // síncrono
const spyAsync = vi.fn().mockResolvedValue(dados);    // Promise resolvida
const spyRx = vi.fn().mockReturnValue(of(dados));     // Observable do RxJS
```

### ⚠️ Diferença crítica de spies (Vitest vs Jasmine)

- **Jasmine**: `spyOn(service, 'metodo')` substitui o método por um stub que retorna `undefined`.
- **Vitest**: `vi.spyOn(service, 'metodo')` **EXECUTA o método original por padrão**. Para substituir o comportamento, use `.mockReturnValue()` ou `.mockImplementation()`.

```typescript
// Para isolar o método real:
vi.spyOn(service, 'salvar').mockResolvedValue({ id: 1 });
```

---

## 4) Async Testing — Zoneless (Angular 21+)

No Angular 21 zoneless, `fakeAsync()` e `waitForAsync()` com Zone.js são desnecessários. Use `async/await` com `fixture.whenStable()` e Fake Timers do Vitest:

```typescript
it('deve avançar timers em testes assíncronos', async () => {
  vi.useFakeTimers();

  component.iniciarDebounce();
  await vi.advanceTimersByTimeAsync(500);  // avança 500ms processando microtasks
  await fixture.whenStable();

  expect(component.executado()).toBe(true);
  vi.useRealTimers();
});
```

---

## 5) Signals Testing

```typescript
import { signal, computed } from '@angular/core';

it('deve atualizar computed quando signal muda', () => {
  const count = signal(0);
  const doubled = computed(() => count() * 2);

  expect(doubled()).toBe(0);
  count.set(5);
  expect(doubled()).toBe(10);
});

it('deve testar input signal de componente', async () => {
  fixture.componentRef.setInput('titulo', 'Novo Título');
  fixture.detectChanges();
  await fixture.whenStable();

  const h1 = fixture.nativeElement.querySelector('h1');
  expect(h1.textContent).toContain('Novo Título');
});
```

---

## 6) HTTP Testing com HttpTestingController

```typescript
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

describe('[Nome]Service — HTTP', () => {
  let service: [Nome]Service;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [[Nome]Service, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject([Nome]Service);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('deve fazer GET e retornar dados', () => {
    service.buscar().subscribe(data => expect(data).toEqual([{ id: 1 }]));
    const req = httpMock.expectOne('/api/[recurso]');
    expect(req.request.method).toBe('GET');
    req.flush([{ id: 1 }]);
  });
});
```

---

## 7) Testes de Snapshot e Coverage

Consulte as diretrizes e ciclo de vida universal de snapshots e coverage em `test-implementation-frontend`.

```typescript
// Snapshot Angular específico
it('deve renderizar componente conforme snapshot', async () => {
  fixture.detectChanges();
  await fixture.whenStable();
  expect(fixture.nativeElement).toMatchSnapshot();
});
```

Diretiva para ignorar linhas específicas no coverage v8:
```typescript
/* v8 ignore next -- @preserve */
```

---

## 8) Comandos com Zero Ruído (R-008 / R-049)

Consulte `test-implementation-frontend` (§6.1) para a política geral de Zero Ruído.

```bash
# Execução silenciosa via Vitest
npx vitest run src/app/features/[caminho]/[nome].spec.ts --silent --reporter=basic 2>&1 | grep -E "FAIL|PASS|Tests" | head -40

# Execução silenciosa via Angular CLI
ng test --include="**/[nome].component.spec.ts" --watch=false --progress=false 2>&1 | grep -E "FAILED|SUCCESS|Executed" | head -40
```

---

## 9) Migração de Jasmine/Karma para Vitest

| Jasmine/Karma | Vitest |
|---|---|
| `jasmine.createSpy()` | `vi.fn()` |
| `spy.and.returnValue(v)` | `spy.mockReturnValue(v)` |
| `spyOn(obj, 'met')` | `vi.spyOn(obj, 'met').mockReturnValue(...)` |
| `fakeAsync(() => { tick(n); })` | `vi.useFakeTimers()` + `vi.advanceTimersByTimeAsync(n)` |
| `waitForAsync(() => {})` | `async () => { await fixture.whenStable(); }` |
| `karma.conf.js` | `vitest.config.ts` |

---

## 10) Diagnóstico Cirúrgico Angular (Test Fixer)

Consulte a metodologia agnóstica em `test-implementation-frontend` (§6.3). Erros específicos de Angular:

| Sintoma do Erro | Causa Provável | Ação de Correção |
|---|---|---|
| `AssertionError: expected spy to have been called` | Signal ou efeito assíncrono não processado | Adicionar `await fixture.whenStable()` ou `TestBed.flushEffects()` |
| `Cannot read properties of undefined (reading 'subscribe')` | Mock de Service não retorna Observable | Usar `vi.fn().mockReturnValue(of(dados))` |
| `NG0100: ExpressionChangedAfterItHasBeenCheckedError` | Mutação síncrona pós-renderização | Inspecionar signals vinculados ao template |
| `TypeError: vi.spyOn is not a function` | Falta de `globals: true` no `vitest.config.ts` | Configurar `globals: true` ou importar `vi` de `'vitest'` |

---

## 11) Testes E2E com Playwright em Angular

Para padrões e boas práticas agnósticas de E2E, consulte `test-implementation-frontend` (§5.1). No Angular, utilize roteamento client-side e asserções web-first:

```typescript
// e2e/specs/fluxo-angular.spec.ts
import { test, expect } from '@playwright/test';

test('deve navegar entre rotas standalone', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('nav-pedidos').click();
  await expect(page).toHaveURL('/pedidos');
  await expect(page.getByTestId('tabela-pedidos')).toBeVisible();
});
```

---

## 12) Anti-padrões

- ❌ Usar `fakeAsync/tick` do `@angular/core/testing` sem Zone.js (incompatível com zoneless).
- ❌ Não chamar `vi.restoreAllMocks()` ou omitir `restoreMocks: true` no `vitest.config.ts`.
- ❌ `vi.spyOn(service, 'metodo')` sem `.mockReturnValue()` esperando que vire stub (diferente do Jasmine).
- ❌ Esquecer `httpMock.verify()` em `afterEach` no `HttpTestingController`.
- ❌ Manter `zone.js` em `polyfills` ao rodar em modo zoneless nativo.

---

## Referências

- [Padrões Genéricos Frontend (Base)](../test-implementation-frontend/SKILL.md)
- Angular Testing Guide: https://angular.dev/guide/testing
- Vitest Documentation: https://vitest.dev/
- AnalogJS Vitest Angular: https://analogjs.org/docs/features/testing/vitest
