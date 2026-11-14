---
name: test-implementation-angular-jasmine
description: "Define diretrizes e padrões para padrões consolidados para implementação de testes em Angular com Jasmine/Karma (runner legado). Use para projetos ainda em Jasmine ou em processo de migração. Para novos projetos Angular 20/21+, prefira test-implementation-angular-vitest. Use quando atuar em angular jasmine, jasmine karma, component test jasmine. Não use para tarefas fora do escopo de test-implementation-angular-jasmine ou implementação direta de código de negócio não relacionado."
tier: 2
category: testing
triggers:
  - "angular jasmine"
  - "jasmine karma"
  - "component test jasmine"
  - "angular e2e jasmine"
  - "ng test jasmine"
  - "migrar jasmine vitest"
  - "angular legacy testing"
source_docs:
  - .github/instructions/angular-v21-frontend.instructions.md
  - .github/skills/test-implementation-frontend/SKILL.md
  - CLAUDE.md
  - .github/copilot-instructions.md
tools: []
---

# Test Implementation — Angular / Jasmine / Karma (Legado)

> ⚠️ **Nota**: Karma foi oficialmente **depreciado** (2023) e Jasmine é o runner legado.
> Para **novos projetos Angular 20/21+**, use `test-implementation-angular-vitest`
> (Vitest é o padrão oficial desde Angular 21).
> Use esta skill para: (a) projetos ainda em Jasmine; (b) migração planejada para Vitest.
>
> Para padrões agnósticos de frontend, consulte `test-implementation-frontend`.

## Quando Usar

- Ativação em cenários de angular jasmine, jasmine karma, component test jasmine.

## Quando NÃO Usar

- Não usar para demandas fora do domínio de `test-implementation-angular-jasmine` ou quando outra skill específica cobrir integralmente o escopo.

## Contexto

Stack de referência:
- **Angular 21** com Signals, Standalone components, Control Flow (`@if`, `@for`)
- **Jasmine + Karma** como test runners nativos
- **Playwright** para testes E2E
- **Istanbul** para relatórios de cobertura (`ng test --code-coverage`)
- **Change Detection OnPush** por padrão (testes mais rápidos)

## 1) Unit Tests — Jasmine + Karma

### Padrão Base (Componente Standalone)

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { [Nome]Component } from './[nome].component';
import { [Nome]Service } from '../services/[nome].service';
import { of, throwError } from 'rxjs';

describe('[Nome]Component', () => {
  let component: [Nome]Component;
  let fixture: ComponentFixture<[Nome]Component>;
  let [nome]Service: jasmine.SpyObj<[Nome]Service>;

  beforeEach(async () => {
    [nome]Service = jasmine.createSpyObj('[Nome]Service', ['metodo1', 'metodo2']);

    await TestBed.configureTestingModule({
      imports: [[Nome]Component], // standalone
      providers: [{ provide: [Nome]Service, useValue: [nome]Service }]
    }).compileComponents();

    fixture = TestBed.createComponent([Nome]Component);
    component = fixture.componentInstance;
  });

  it('deve renderizar título quando carregado', () => {
    fixture.detectChanges();
    const el = fixture.debugElement.query(By.css('h1'));
    expect(el.nativeElement.textContent).toContain('Título');
  });

  it('deve chamar serviço quando ação disparada', () => {
    [nome]Service.metodo1.and.returnValue(of(dados));
    component.ngOnInit();
    expect([nome]Service.metodo1).toHaveBeenCalled();
  });

  it('deve exibir mensagem de erro quando serviço falhar', () => {
    [nome]Service.metodo1.and.returnValue(throwError(() => new Error('erro')));
    component.ngOnInit();
    fixture.detectChanges();
    expect(component.erro).toBeTruthy();
  });
});
```

### Checklist de Unit Test

- [ ] Todos os métodos públicos testados (happy path + edge cases)
- [ ] Dependências mockadas com `jasmine.createSpyObj`
- [ ] HTTP/async com `HttpTestingController` ou `fakeAsync`
- [ ] Signals testados com `TestBed.flushEffects()`
- [ ] `fixture.detectChanges()` após modificação de state
- [ ] Cobertura: ≥ 80% linhas, ≥ 70% ramos

### HTTP Testing (HttpClientTestingModule)

```typescript
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

it('deve fazer requisição GET e retornar dados', () => {
  const mockData = { id: 1, nome: 'Teste' };
  
  TestBed.configureTestingModule({
    imports: [HttpClientTestingModule, [Nome]Component],
    providers: [[Nome]Service]
  });

  const service = TestBed.inject([Nome]Service);
  const httpMock = TestBed.inject(HttpTestingController);

  service.buscarDados().subscribe(data => {
    expect(data).toEqual(mockData);
  });

  const req = httpMock.expectOne('/api/dados');
  expect(req.request.method).toBe('GET');
  req.flush(mockData);
  httpMock.verify();
});
```

### Async/Promises — fakeAsync (preferido)

```typescript
it('deve completar operação assíncrona', fakeAsync(() => {
  let resultado: string;
  component.metodoAssincrono().subscribe(r => resultado = r);
  expect(resultado).toBeUndefined();
  
  tick(1000); // avança tempo simulado
  expect(resultado).toBe('completado');
}));
```

### Signals Testing (Angular 17+)

```typescript
it('deve atualizar computed signal quando input muda', () => {
  const count = signal(0);
  const doubled = computed(() => count() * 2);
  
  expect(doubled()).toBe(0);
  count.set(5);
  expect(doubled()).toBe(10);
});

it('deve disparar effect quando sinal muda', fakeAsync(() => {
  let executado = false;
  const valor = signal(0);
  
  effect(() => { if (valor() > 0) executado = true; });
  
  TestBed.flushEffects();
  expect(executado).toBe(false);
  
  valor.set(1);
  TestBed.flushEffects();
  expect(executado).toBe(true);
}));
```

## 2) Integration Tests

- Configurar `ActivatedRoute` mockado e `ReactiveFormsModule` para testes de integração de componentes/rotas.

## 3) E2E Tests — Playwright

- Estruturar testes E2E com Page Objects, seletores acessíveis (`getByRole`) e auto-waiting nativo.
- Exemplos completos de código em [`references/detailed-patterns-and-examples.md`](references/detailed-patterns-and-examples.md).

## 4) Coverage Targets

| Métrica | Mínimo | Ideal |
|---|---|---|
| Linhas | 70% | 80%+ |
| Ramos | 60% | 70%+ |
| Funções | 75% | 85%+ |
| Statements | 70% | 80%+ |

## 5) Comandos Angular / Istanbul

> **Zero-Noise Test Policy (R-008 / R-049)**: Sempre desativar watch e progresso, e filtrar saída via pipe ou executar via `ctx_execute` (Think-in-Code).

### A) Via `ctx_execute` (Think-in-Code — Recomendado)

```javascript
const { execSync } = require('child_process');
try {
  const out = execSync("ng test --include='**/[nome].component.spec.ts' --watch=false --progress=false --no-color", { encoding: 'utf8' });
  console.log(out.trim());
} catch (err) {
  const full = (err.stdout || '') + '\n' + (err.stderr || '');
  console.log(full.split('\n').filter(l => /(FAILED|Executed|Error:)/i).slice(0, 30).join('\n'));
}
```

### B) Via Terminal com Filtro Obrigatório

```bash
# Arquivo específico (sem watch, sem progresso, filtrado)
ng test --include='**/[nome].component.spec.ts' --watch=false --progress=false --no-color 2>&1 | grep -E "FAILED|SUCCESS|Executed" | head -40

# Unit tests com coverage
ng test --code-coverage --watch=false --progress=false --no-color 2>&1 | grep -E "FAILED|SUCCESS|Executed|TOTAL" | head -40

# CI mode
npm run test-ci 2>&1 | grep -E "FAILED|SUCCESS|Executed" | head -40
```

## 6) Anti-padrões

- ❌ Não usar `jasmine.createSpyObj` para dependências (mocks parciais frágeis)
- ❌ Não chamar `fixture.detectChanges()` após setup (UI desatualizada)
- ❌ Usar `setTimeout` em testes (use `fakeAsync` + `tick`)
- ❌ Seletores CSS instáveis em E2E (prefira `data-testid`)
- ❌ Cobertura <70% sem negociação explícita

## 7) Comandos Rápidos

```bash
# Watch mode (desenvolvimento local)
ng test

# Coverage completo
ng test --code-coverage

# E2E headless
npx playwright test --reporter=html

# Listar testes sem executar
ng test --list
```

## Referências

- Angular Testing Guide: https://angular.io/guide/testing
- Jasmine: https://jasmine.github.io/
- Playwright: https://playwright.dev/
- Karma: https://karma-runner.github.io/
- [Padrões Genéricos Frontend (Base)](../test-implementation-frontend/SKILL.md)

## Checklist de Conformidade

- [ ] Diretrizes, contratos e restrições de escopo de `test-implementation-angular-jasmine` verificados e atendidos.
