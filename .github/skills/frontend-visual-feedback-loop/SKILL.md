---
name: frontend-visual-feedback-loop
description: >-
  Diretrizes e padrões canônicos para executar o Visual Feedback Loop (VFL) em
  interfaces frontend de qualquer framework (Angular, React, Vue, Svelte) via
  renderização isolada (Storybook/dev-server), inspeção multimodal multi-viewport
  (375px/768px/1440px), Árvore de Acessibilidade (AOM) e asserções com Playwright.
  Não use para testes de lógica pura sem camada visual.
tier: 2
category: quality
triggers:
  - "feedback visual frontend"
  - "inspecionar layout com screenshot"
  - "visual feedback loop"
  - "playwright visual verification"
  - "validar layout multi-viewport"
  - "inspecionar arvore acessibilidade aom"
source_docs:
  - CLAUDE.md
  - .github/copilot-instructions.md
  - .github/skills/frontend-componentization-patterns/SKILL.md
  - .github/skills/design-system-component-contracts/SKILL.md
tools: []
---

# Frontend Visual Feedback Loop

## 0) Problema Resolvido & Princípios Fundamentais

> **Arquitetura da Skill (Anthropic Open Spec / Progressive Disclosure)**:
> - **Nível 1 (Metadados)**: Frontmatter com `name`, `description`, `tier`, `category` e `triggers` para descoberta e roteamento rápido.
> - **Nível 2 (Corpo Operacional)**: Este arquivo `SKILL.md` contendo regras essenciais, processo canônico, exemplos contrastantes e checklist.
> - **Nível 3 (Recursos Suplementares)**: Pastas opcionais `references/`, `scripts/` e `snippets/` com exemplos de código longos (> 8 linhas, conforme R-026).

Testes unitários e compilação headless operam na memória e não executam o motor de layout do browser. Erros como colapso de flexbox, textos literais de ícone vazando, diálogos sem scroll e quebra em mobile passam invisíveis pelos testes automatizados tradicionais.

Esta skill formaliza o **Visual Feedback Loop (VFL)** agnóstico de framework:
1. **Renderização Isolada (Component-Driven)**: Renderizar em sandbox (Storybook ou dev-server) sem acoplamento a backend.
2. **Dupla Representação**: Árvore de Acessibilidade (AOM) para estrutura semântica + Screenshots em 3 viewports canônicos (375px, 768px, 1440px).
3. **Economia de Contexto (Think-in-Code)**: Salvar imagens em disco e extrair métricas de bounding box e estilos computados (`getComputedStyle`), sem poluir a janela de chat com bytes de imagem.
4. **Loop Finito (Circuit Breaker)**: Máximo de 2 iterações de auto-correção visual antes de escalar para decisão humana.

---

## 1) Quando Usar vs Quando NÃO Usar

### ✅ Quando Usar
- Ao implementar ou refatorar telas, diálogos, formulários e componentes visuais em qualquer framework (Angular, React, Vue, Svelte).
- Para validar responsividade e quebras em breakpoints padronizados (mobile 375px, tablet 768px, desktop 1440px).
- Para auditar se elementos utilizam tokens semânticos do Design System em vez de cores hexadecimais inline.
- Como base de conhecimento para o Gate 2 de Paridade Visual do `WORKFLOW-FEATURE-DEVELOPMENT`.
- Como método de validação primário para agentes focados em UI e estilização (`ui-stylist`), os quais são **isentos** de criar ou rodar testes unitários.

### ❌ Quando NÃO Usar
- Para testes unitários de lógica de negócio, cálculo matemático, stores ou services puros (usar `test-implementation-*`).
- Para migrações de banco de dados ou endpoints REST (usar `database-specialist` ou `integration-contract-analysis`).
- Em correções exclusivamente textuais sem impacto visual ou estrutural.

---

## 2) Diretrizes Operacionais e Processo Canônico

O ciclo VFL opera em 4 etapas sequenciais:

### Etapa 1: Sandbox e Renderização Isolada
1. Executar o componente em sandbox (Storybook ou harness local de rota efêmera).
2. Garantir renderização dos estados críticos: default, preenchido, vazio (`empty-state`), loading e erro.

### Etapa 2: Captura Multi-Viewport e Snapshot Semântico
1. Disparar automação headless via Playwright nos viewports canônicos: `375x667` (mobile), `768x1024` (tablet) e `1440x900` (desktop).
2. Extrair o snapshot da Árvore de Acessibilidade (AOM) para validação de nós interativos e labels acessíveis.

### Etapa 3: Auditoria Visual e Critic Loop
1. Validar que elementos de ícone não contenham texto literal desprovido de renderização de glifo/SVG.
2. Checar que diálogos e containers utilizam classes utilitárias de scroll e grid responsivo.
3. Inspecionar estilos computados (`getComputedStyle`) para barrar cores hexadecimais inline fora do tema.
4. Se houver divergência: aplicar correção cirúrgica e re-executar (limite rígido: 2 iterações).

### Etapa 4: Quality Gate de UI
1. Anexar evidências resumidas (viewports validados, conformidade AOM e tokens verificados) ao relatório do Gate 2.

---

## 3) Padrões Canônicos com Exemplos Contrastantes

### Padrão 1: Inspeção Semântica via Árvore de Acessibilidade (AOM)

#### ❌ Anti-padrão (Texto de ícone vazando silenciosamente)
```html
<!-- ❌ Nome do ícone tratado como texto cru pelo browser -->
<button class="btn-icon">
  close
</button>
```
*Problema*: Em testes headless o botão existe no DOM, mas visualmente a palavra "close" vaza sem o glifo do ícone.

#### ✅ Padrão Canônico (Wrapper com papel acessível e SVG/glifo)
```html
<!-- ✅ Wrapper padronizado com label acessível explícito -->
<button class="btn-icon" aria-label="Fechar">
  <app-svg-icon name="close" aria-hidden="true" />
</button>
```
*Benefício*: A árvore AOM registra role="button" com nome "Fechar", e o SVG é renderizado sem vazamento de texto.

---

### Padrão 2: Envelopamento de Diálogos e Grids Responsivos

#### ❌ Anti-padrão (Dimensões fixas inline e empilhamento rígido)
```html
<!-- ❌ Largura fixa arbitrária sem controle de scroll -->
<div style="width: 540px; height: 700px;">
  <input class="full-field" />
  <input class="full-field" />
</div>
```
*Problema*: Quebra em viewports mobile (overflow horizontal) e não rola em viewports de altura reduzida.

#### ✅ Padrão Canônico (Classes utilitárias de layout e grid de 2 colunas)
```html
<!-- ✅ Layout elástico com classes utilitárias do Design System -->
<div class="app-dialog-content">
  <div class="form-grid">
    <app-form-field label="Campo 1" />
    <app-form-field label="Campo 2" />
  </div>
</div>
```
*Benefício*: Adaptação automática a 1 coluna em mobile (375px) e 2 colunas em desktop, com scroll gerenciado.

---

### Padrão 3: Consumo de Cores por Design Tokens

#### ❌ Anti-padrão (Hexadecimal arbitrário inline em SCSS de feature)
```scss
// ❌ Cor hardcoded fora da paleta do tema
.custom-card {
  background-color: #1976d2;
  border: 1px solid #e0e0e0;
}
```
*Problema*: Desalinhamento cromático com o tema corporativo e incompatibilidade com temas dark/light.

#### ✅ Padrão Canônico (Variáveis CSS e tokens semânticos)
```scss
// ✅ Tokens de tema desacoplados e auditáveis
.custom-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
}
```
*Benefício*: Paridade estética imediata, suporte a temas e ausência de regressões cromáticas.

---

## 4) Checklist de Auto-Verificação

- [ ] Componente renderizado e inspecionado em 3 viewports canônicos (375px, 768px, 1440px).
- [ ] Árvore de acessibilidade (AOM) sem vazamento de texto literal em tags de ícones.
- [ ] Diálogos utilizam classes utilitárias de scroll e padding do projeto sem larguras fixas inline.
- [ ] Estados vazios (`empty-state`) envelopados para ocupar a largura total do container de seção.
- [ ] Arquivos SCSS auditados: zero cores hexadecimais inline (`#[0-9a-fA-F]{3,6}`) fora de tokens.
- [ ] Nenhum bloco de código inline nesta skill ultrapassa 8 linhas (R-026).

---

## 5) Referências

- Playwright MCP Server & CLI: https://github.com/microsoft/playwright-mcp
- Component Story Format (CSF3) — Storybook: https://storybook.js.org/docs/api/csf
- W3C Design Tokens Community Group: https://design-tokens.github.io/community-group/format/
- Anthropic Agentic Coding Handbook — Visual Feedback Workflow (2025/2026).
- W3C WAI-ARIA Accessibility Tree (AOM) Specification.
