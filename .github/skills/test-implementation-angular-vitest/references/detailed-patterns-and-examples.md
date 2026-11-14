# Test Implementation — Angular + Vitest (Setup e Exemplos Avançados)

## 1) Setup Completo — Configuração Nativa Angular 20+ (`angular.json`, `tsconfig.spec.json`, `vitest.config.ts`)

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

## 6–7) HTTP Testing (`HttpTestingController`), Snapshot e Coverage

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
