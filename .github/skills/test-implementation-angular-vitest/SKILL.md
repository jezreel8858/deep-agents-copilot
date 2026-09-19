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
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/instructions/angular-v21-frontend.instructions.md
  - .github/skills/test-implementation-frontend/SKILL.md
  - .github/skills/test-coverage-governance/SKILL.md
tools: []
---

# Test Implementation — Angular + Vitest

> **Escopo**: implementação específica para **Angular 20/21+ com Vitest** como test runner oficial.
> Para padrões agnósticos de frontend, consulte `test-implementation-frontend`.
> Para padrões com Jasmine/Karma (legado), consulte `test-implementation-angular-jasmine`.

## Contexto

A partir do **Angular 20**, o suporte nativo ao Vitest foi introduzido de forma experimental via builder `@angular/build:unit-test`. No **Angular 21** o suporte tornou-se **estável e padrão** para novos projetos — ao rodar `ng new`, Vitest é sugerido como opção padrão e Karma/Jasmine são considerados legado.

**Por que Vitest:**
- Baseado em Vite — startup ultra-rápido (HMR nativo)
- Modo watch instantâneo com hot reload de testes
- API 100% compatível com Jest (`describe`, `it`, `expect`, `vi.fn()`)
- `globals: true` → sem imports de `describe`/`it`/`expect` em cada arquivo
- Suporte nativo a TypeScript sem transpilação extra
- Coverage com provider `v8` (veloz) ou `istanbul` (preciso)

**Karma foi oficialmente depreciado em 2023.** Jasmine segue sendo suportado como runner alternativo, mas Vitest é o caminho oficial de novos projetos Angular 20+.

---

## 1) Setup — Configuração Nativa Angular 20+

### Dependências

```bash
# Instalação mínima (happy-dom é detectado automaticamente pelo Angular CLI)
npm install -D vitest happy-dom

# Para coverage
npm install -D @vitest/coverage-v8

# Alternativa de ambiente DOM (fallback se happy-dom não estiver instalado)
npm install -D jsdom
```

> **Nota**: `happy-dom` é preferido por ser mais rápido. O Angular CLI detecta automaticamente qual está instalado. Se ambos estiverem, `happy-dom` tem precedência.

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

### vitest.config.ts (configuração estendida — opcional)

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,                          // describe/it/expect sem imports
    environment: 'happy-dom',              // ou 'jsdom'
    setupFiles: ['src/test-setup.ts'],     // se necessário setup adicional
    include: ['src/**/*.spec.ts'],
    restoreMocks: true,                    // ✅ limpa vi.spyOn/vi.fn após cada teste
    clearMocks: true,                      // limpa mock.calls entre testes
    coverage: {
      provider: 'v8',                      // v8 (rápido) ou 'istanbul' (preciso)
      reporter: ['text', 'html', 'lcov'],
      reportsDirectory: 'coverage',
      thresholds: {
        statements: 80,
        branches: 70,
        functions: 80,
        lines: 80,
      },
      exclude: [
        'src/environments/**',
        '**/*.config.ts',
        '**/*.module.ts',
        'src/main.ts',
      ],
    },
  },
});
```

**Referenciando o config no angular.json:**

```json
"options": {
  "runner": "vitest",
  "runnerConfig": "vitest.config.ts"
}
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
  let [nome]Service: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [[Nome]Component],  // standalone
      providers: [
        {
          provide: [Nome]Service,
          useValue: {
            buscar: vi.fn().mockResolvedValue([{ id: 1, nome: 'Teste' }]),
            salvar: vi.fn().mockResolvedValue({ id: 2 }),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent([Nome]Component);
    component = fixture.componentInstance;
    [nome]Service = TestBed.inject([Nome]Service) as any;
  });

  it('deve criar o componente', () => {
    expect(component).toBeTruthy();
  });

  it('deve carregar dados ao inicializar', async () => {
    fixture.detectChanges();
    await fixture.whenStable();  // aguarda efeitos assíncronos (zoneless)

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

### Checklist de Unit Test

- [ ] `TestBed.configureTestingModule` com imports do componente standalone
- [ ] Dependências mockadas via `providers` + `useValue` com `vi.fn()`
- [ ] `fixture.detectChanges()` após setup do estado inicial
- [ ] `await fixture.whenStable()` para efeitos assíncronos (zoneless)
- [ ] Happy path + edge cases + error path testados
- [ ] `restoreMocks: true` configurado no vitest.config.ts

### 2.2) Component Harnesses (`@angular/cdk/testing`)

O uso de Component Harnesses desacopla os testes da estrutura interna do DOM do componente (evitando quebras por mudanças em classes CSS ou tags):

```typescript
import { TestbedHarnessEnvironment } from '@angular/cdk/testing/testbed';
import { MatButtonHarness } from '@angular/material/button/testing';
import { HarnessLoader } from '@angular/cdk/testing';

describe('[Nome]Component com Harness', () => {
  let loader: HarnessLoader;
  let fixture: ComponentFixture<[Nome]Component>;

  beforeEach(async () => {
    // ... TestBed setup ...
    fixture = TestBed.createComponent([Nome]Component);
    loader = TestbedHarnessEnvironment.loader(fixture);
    fixture.detectChanges();
  });

  it('deve disparar clique via Harness', async () => {
    const botaoSalvar = await loader.getHarness(
      MatButtonHarness.with({ text: 'Salvar' })
    );

    expect(await botaoSalvar.isDisabled()).toBe(false);
    await botaoSalvar.click();

    await fixture.whenStable();
    // asserções de efeito...
  });
});
```

---

## 3) Mocking — vi.fn() e vi.spyOn()

### vi.fn() — substitui jasmine.createSpy()

```typescript
// Jasmine (legado)
const spy = jasmine.createSpy('meuMetodo').and.returnValue(of(dados));

// Vitest (moderno)
const spy = vi.fn().mockReturnValue(dados);           // retorno síncrono
const spy = vi.fn().mockResolvedValue(dados);          // retorno assíncrono (Promise)
const spy = vi.fn().mockReturnValueOnce(dados).mockReturnValue(null); // uma vez e depois padrão
const spy = vi.fn().mockImplementation((id) => ({ id, nome: 'Mock' })); // implementação customizada
const spy = vi.fn().mockRejectedValue(new Error('erro')); // rejeitar Promise

// Com nome descritivo (melhor feedback no output)
const spy = vi.fn().mockName('buscarUsuario');
```

### ⚠️ Diferença crítica: comportamento padrão de spies

```typescript
// JASMINE: spy retorna undefined por padrão (não chama o original)
spyOn(service, 'metodo'); // NÃO chama implementação real

// VITEST: vi.spyOn() EXECUTA a implementação original por padrão
vi.spyOn(service, 'metodo'); // ← CHAMA a implementação real!

// Para substituir (equivalente ao Jasmine):
vi.spyOn(service, 'metodo').mockReturnValue(dadosFalsos);
```

### vi.spyOn() — espionar métodos existentes

```typescript
it('deve chamar serviço com parâmetros corretos', () => {
  const spy = vi.spyOn([nome]Service, 'salvar').mockResolvedValue({ id: 1 });

  component.salvar({ campo: 'valor' });

  expect(spy).toHaveBeenCalledWith({ campo: 'valor' });
  expect(spy).toHaveBeenCalledOnce();
});
```

### Verificação de chamadas

```typescript
// Quantas vezes foi chamado
expect(spy).toHaveBeenCalledTimes(2);
expect(spy).toHaveBeenCalledOnce();  // equivalente a toHaveBeenCalledTimes(1)

// Com quais argumentos
expect(spy).toHaveBeenCalledWith({ id: 1, nome: 'Teste' });
expect(spy).toHaveBeenLastCalledWith({ id: 2 });

// Nunca foi chamado
expect(spy).not.toHaveBeenCalled();

// Inspecionar chamadas individualmente
expect(spy.mock.calls[0][0]).toEqual({ id: 1 });  // primeira chamada, primeiro argumento
```

### Limpeza de mocks entre testes

```typescript
// Opção 1 (PREFERIDA): configurar no vitest.config.ts
// restoreMocks: true — restaura implementação original após cada teste
// clearMocks: true — limpa mock.calls entre testes

// Opção 2: manual em afterEach
afterEach(() => {
  vi.restoreAllMocks();  // restaura implementações originais
  vi.clearAllMocks();    // limpa calls/instances sem restaurar
});
```

---

## 4) Async Testing — Zoneless (Angular 21+)

> **Atenção**: Angular 21 é zoneless por padrão. `fakeAsync()` e `waitForAsync()` de `@angular/core/testing` **não funcionam** sem Zone.js.

### async/await (substitui waitForAsync)

```typescript
// ANTES (Zone.js)
it('deve carregar dados', waitForAsync(() => {
  component.ngOnInit();
  fixture.whenStable().then(() => {
    expect(component.dados).toBeDefined();
  });
}));

// AGORA (zoneless)
it('deve carregar dados', async () => {
  fixture.detectChanges();
  await fixture.whenStable();
  expect(component.dados()).toBeDefined();
});
```

### Vitest Fake Timers (substitui fakeAsync/tick)

```typescript
import { vi } from 'vitest';

it('deve executar após timeout', async () => {
  vi.useFakeTimers();

  let executado = false;
  setTimeout(() => { executado = true; }, 3000);

  expect(executado).toBe(false);
  await vi.advanceTimersByTimeAsync(3000);  // avança 3s (async-aware)
  expect(executado).toBe(true);

  vi.useRealTimers();  // restaurar sempre após o teste
});

// Ou usando flush (avança TODOS os timers pendentes):
it('deve completar todos os timers pendentes', async () => {
  vi.useFakeTimers();
  // ... setup
  await vi.runAllTimersAsync();
  // ... assert
  vi.useRealTimers();
});
```

> **Nota**: use `vi.advanceTimersByTimeAsync` (com `Async`) no contexto zoneless para garantir que microtasks sejam processadas corretamente.

---

## 5) Signals Testing

```typescript
import { signal, computed, effect } from '@angular/core';

it('deve atualizar computed quando signal muda', () => {
  const count = signal(0);
  const doubled = computed(() => count() * 2);

  expect(doubled()).toBe(0);
  count.set(5);
  expect(doubled()).toBe(10);
});

it('deve disparar effect quando signal muda', async () => {
  let valorCapturado = 0;
  const valor = signal(0);

  TestBed.runInInjectionContext(() => {
    effect(() => { valorCapturado = valor(); });
  });

  await fixture.whenStable();  // processa effect inicial
  expect(valorCapturado).toBe(0);

  valor.set(42);
  await fixture.whenStable();  // processa effect após mudança
  expect(valorCapturado).toBe(42);
});

it('deve testar input signal de componente', async () => {
  // Angular 17+ input signals
  fixture.componentRef.setInput('titulo', 'Novo Título');
  fixture.detectChanges();
  await fixture.whenStable();

  const h1 = fixture.nativeElement.querySelector('h1');
  expect(h1.textContent).toContain('Novo Título');
});
```

---

## 6) HTTP Testing

```typescript
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

describe('[Nome]Service — HTTP', () => {
  let service: [Nome]Service;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        [Nome]Service,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject([Nome]Service);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());  // garante que não há requisições pendentes

  it('deve fazer GET e retornar dados', () => {
    const mockData = [{ id: 1, nome: 'Item' }];

    service.buscar().subscribe(data => {
      expect(data).toEqual(mockData);
    });

    const req = httpMock.expectOne('/api/[recurso]');
    expect(req.request.method).toBe('GET');
    req.flush(mockData);
  });

  it('deve tratar erro HTTP 500', () => {
    service.buscar().subscribe({
      error: (err) => expect(err.status).toBe(500),
    });

    httpMock.expectOne('/api/[recurso]').flush('Erro', { status: 500, statusText: 'Server Error' });
  });
});
```

---

## 7) Testes de Serviço (sem componente)

```typescript
describe('[Nome]Service', () => {
  let service: [Nome]Service;
  let dependencia: { metodo: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    dependencia = { metodo: vi.fn().mockResolvedValue('resultado') };

    TestBed.configureTestingModule({
      providers: [
        [Nome]Service,
        { provide: [Dependencia], useValue: dependencia },
      ],
    });

    service = TestBed.inject([Nome]Service);
  });

  it('deve processar e retornar resultado transformado', async () => {
    const resultado = await service.processar('entrada');

    expect(dependencia.metodo).toHaveBeenCalledWith('entrada');
    expect(resultado).toBe('RESULTADO');  // se serviço transforma para uppercase
  });

  it('deve lançar erro quando dependência falhar', async () => {
    dependencia.metodo.mockRejectedValue(new Error('Falha'));

    await expect(service.processar('entrada')).rejects.toThrow('Falha');
  });
});
```

---

## 8) Snapshot Tests

```typescript
it('deve renderizar componente conforme snapshot', async () => {
  fixture.detectChanges();
  await fixture.whenStable();

  // Cria/compara snapshot do HTML renderizado
  expect(fixture.nativeElement).toMatchSnapshot();
});
```

> Snapshots são salvos em `__snapshots__/[nome].spec.ts.snap`. Adicionar ao Git.
> Para atualizar snapshots: `ng test -- --update-snapshots` ou `vitest --update-snapshots`.

---

## 9) Coverage — @vitest/coverage-v8

### Configuração (vitest.config.ts)

```typescript
coverage: {
  provider: 'v8',
  reporter: ['text', 'html', 'lcov'],
  reportsDirectory: 'coverage',
  thresholds: {
    statements: 80,
    branches: 70,
    functions: 80,
    lines: 80,
    // Thresholds específicos por módulo
    'src/app/core/**/*.ts': { statements: 90, branches: 85 },
  },
  exclude: [
    'src/environments/**',
    'src/main.ts',
    '**/*.config.ts',
    '**/*.module.ts',
    '**/*.routes.ts',
  ],
}
```

### Excluir código específico do coverage

```typescript
/* v8 ignore next -- @preserve */
if (environment.production) {
  console.log('Produção');
}

/* v8 ignore next 3 -- @preserve */
function codigoNaoTestavel() {
  // Linhas ignoradas
}
```

---

## 10) Comandos

> **Zero-Noise Test Policy (R-008 / R-049)**: Nunca rodar comandos de teste interativos ou bare. Use flags silenciosas (`--silent`, `--reporter=basic`) e filtros pipe, ou execute via `ctx_execute` (Think-in-Code).

### A) Via `ctx_execute` (Think-in-Code — Recomendado)

```javascript
const { execSync } = require('child_process');
try {
  const out = execSync('npx vitest run src/app/features/[caminho]/[nome].spec.ts --silent --reporter=basic', { encoding: 'utf8' });
  console.log(out.trim());
} catch (err) {
  const full = (err.stdout || '') + '\n' + (err.stderr || '');
  console.log(full.split('\n').filter(l => /(FAIL|Error:|Tests.*failed)/i).slice(0, 30).join('\n'));
}
```

### B) Via Terminal com Filtro Obrigatório

```bash
# Arquivo específico via Vitest (silencioso e sem watch)
npx vitest run src/app/features/[caminho]/[nome].spec.ts --silent --reporter=basic 2>&1 | grep -E "FAIL|PASS|Tests" | head -40

# Arquivo específico via Angular CLI (sem watch, sem progresso)
ng test --include="**/[nome].component.spec.ts" --watch=false --progress=false 2>&1 | grep -E "FAILED|SUCCESS|Executed" | head -40

# Coverage conciso
npx vitest run --coverage --silent --reporter=basic 2>&1 | grep -E "FAIL|PASS|All files|TOTAL" | head -40

# Em PowerShell / Windows:
npx vitest run src/app/features/[caminho]/[nome].spec.ts --silent --reporter=basic
```

---

## 11) Migração de Jasmine/Karma

| Jasmine/Karma | Vitest |
|---|---|
| `jasmine.createSpy()` | `vi.fn()` |
| `spy.and.returnValue(v)` | `spy.mockReturnValue(v)` |
| `spy.and.returnValue(of(v))` | `spy.mockReturnValue(of(v))` |
| `spy.and.callFake(fn)` | `spy.mockImplementation(fn)` |
| `spyOn(obj, 'met')` | `vi.spyOn(obj, 'met')` |
| `expect(spy).toHaveBeenCalled()` | `expect(spy).toHaveBeenCalled()` ✓ (igual) |
| `expect(spy).toHaveBeenCalledTimes(n)` | `expect(spy).toHaveBeenCalledTimes(n)` ✓ |
| `fakeAsync(() => { ... tick(1000); })` | `vi.useFakeTimers()` + `vi.advanceTimersByTimeAsync(1000)` |
| `waitForAsync(() => { ... })` | `async () => { await fixture.whenStable(); }` |
| `jasmine.clock().install()` | `vi.useFakeTimers()` |
| `jasmine.clock().tick(n)` | `vi.advanceTimersByTimeAsync(n)` |
| `afterEach(() => { ... })` | `afterEach(() => { vi.restoreAllMocks(); })` |
| `karma.conf.js` + `angular.json test: karma` | `vitest.config.ts` + `angular.json test: @angular/build:unit-test` |

### Script de migração automática (Angular CLI schematic)

```bash
# Aplicar schematic de migração oficial (quando disponível)
ng generate @angular/core:migrate-to-vitest

# Alternativa via AnalogJS
ng generate @analogjs/vitest-angular:setup
```

---

## 11.1) Diagnóstico e Correção de Falhas (Test Fixer)

Diretrizes cirúrgicas para correção de testes quebrados em Angular (sem alterar regras de produção):

| Sintoma do Erro | Causa Provável | Ação de Correção |
|---|---|---|
| `AssertionError: expected spy to have been called` | Efeito/Signal assíncrono não processado | Adicionar `await fixture.whenStable()` ou `TestBed.flushEffects()` antes do `expect` |
| `Cannot read properties of undefined (reading 'subscribe')` | Mock de Service não retorna Observable | Configurar mock com `of(valor)` do RxJS: `vi.fn().mockReturnValue(of(dados))` |
| `NG0100: ExpressionChangedAfterItHasBeenCheckedError` | Mutação de estado síncrona pós-renderização | Revisar fluxo de atualização ou disparar `fixture.detectChanges()` imediatamente após evento |
| `Error: Expected 1 matching element, found 0` | Renderização dependente de `@if` assíncrono | Aguardar Promise/Signal resolver (`await fixture.whenStable()`) antes de consultar o DOM |
| `TypeError: vi.spyOn is not a function` | Configuração de Vitest sem `globals: true` | Importar `vi` de `'vitest'` ou habilitar `globals: true` no `vitest.config.ts` |

---

## 11.2) Testes E2E com Playwright em Aplicações Angular

Para validação de jornadas completas de usuário com browsers reais:

```typescript
// e2e/specs/login.spec.ts
import { test, expect } from '@playwright/test';

test('deve autenticar e redirecionar para tela principal', async ({ page }) => {
  await page.goto('/login');

  // Seletores semânticos resilientes
  await page.getByTestId('input-email').fill('usuario@exemplo.com');
  await page.getByTestId('input-senha').fill('senha123');
  await page.getByRole('button', { name: 'Entrar' }).click();

  // Asserção web-first com auto-wait
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByTestId('painel-resumo')).toBeVisible();
});
```

---

## 12) Anti-padrões

- ❌ Usar `fakeAsync/tick` sem Zone.js (não funciona em zoneless)
- ❌ Não chamar `vi.restoreAllMocks()` — spies vazam entre testes
- ❌ Não usar `restoreMocks: true` no config e esquecer cleanup manual
- ❌ `vi.spyOn(service, 'metodo')` sem `.mockReturnValue()` — chama implementação real (diferente do Jasmine!)
- ❌ Não chamar `httpMock.verify()` em `afterEach` (requisições pendentes não detectadas)
- ❌ Usar `snapshot` para testes de comportamento (use apenas para output de HTML estruturado)
- ❌ Misturar `globals: true` e imports explícitos (`import { describe } from 'vitest'`) no mesmo projeto
- ❌ Não remover `zone.js` de `polyfills` ao migrar para zoneless (conflito)

---

## 13) Estrutura de Arquivos

```
src/
  app/
    [feature]/
      [nome].component.ts
      [nome].component.spec.ts      ← testes do componente
      [nome].service.ts
      [nome].service.spec.ts        ← testes do serviço
  test-providers.ts                 ← providers globais (provideZonelessChangeDetection)
  test-setup.ts                     ← setup adicional se necessário

vitest.config.ts                    ← config estendida (opcional)
coverage/                           ← relatórios de coverage
__snapshots__/                      ← snapshots gerados (commitar no Git)
```

---

## Referências

- Angular Testing com Vitest (Tim Deschryver): https://timdeschryver.dev/blog/angular-testing-library-with-vitest
- Vitest + Angular 21 — Migração (angular.schule): https://angular.schule/blog/2025-11-migrate-to-vitest
- Angular University — Modern Vitest: https://blog.angular-university.io/angular-testing-vitest
- Docs Vitest Coverage: https://vitest.dev/guide/coverage
- Analog JS Vitest Angular: https://analogjs.org/docs/features/testing/vitest
- Angular Component Testing Scenarios: https://angular.dev/guide/testing/components-scenarios

